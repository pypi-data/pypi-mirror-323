import io
import os
import re
import signal
import socket
import struct
import subprocess
from enum import Enum
from time import sleep
from typing import Tuple, Optional, Union, List, Any, Dict

import gymnasium as gym
import numpy as np
import psutil
from PIL import Image, ImageDraw
from gymnasium import spaces
from gymnasium.core import ActType, ObsType, RenderFrame
import torch

from .action_space import ActionSpace
from .buffered_socket import BufferedSocket
from .csv_logger import CsvLogger, LogBackend
from .font import get_font
from .initial_environment_config import InitialEnvironmentConfig
from .minecraft import (
    wait_for_server,
    send_fastreset2,
    send_action_and_commands,
    send_exit,
)
from .print_with_time import print_with_time
from .proto import observation_space_pb2
from .screen_encoding_modes import ScreenEncodingMode


class ActionSpaceVersion(Enum):
    V1_MINEDOJO = 1
    V2_MINERL_HUMAN = 2


class ObservationTensorType(Enum):
    NONE = 0
    CUDA_DLPACK = 1
    APPLE_TENSOR = 2


class CraftGroundEnvironment(gym.Env):
    def __init__(
        self,
        initial_env: InitialEnvironmentConfig,
        action_space_version: ActionSpaceVersion = ActionSpaceVersion.V1_MINEDOJO,
        verbose=False,
        env_path=None,
        port=8000,
        find_free_port: bool = True,
        render_action: bool = False,
        render_alternating_eyes: bool = False,
        use_terminate: bool = False,
        cleanup_world: bool = True,  # removes the world when the environment is closed
        use_vglrun: bool = False,  # use vglrun to run the server (headless 3d acceleration)
        track_native_memory: bool = False,
        ld_preload: Optional[str] = None,
        native_debug: bool = False,
        verbose_python: bool = False,
        verbose_gradle: bool = False,
        verbose_jvm: bool = False,
        profile: bool = False,
    ):
        self.action_space_version = action_space_version
        if action_space_version == ActionSpaceVersion.V1_MINEDOJO:
            self.action_space = ActionSpace(6)
        elif action_space_version == ActionSpaceVersion.V2_MINERL_HUMAN:
            self.action_space = gym.spaces.Dict(
                {
                    "attack": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "back": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "forward": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "jump": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "left": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "right": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "sneak": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "sprint": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "use": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "drop": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "inventory": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "hotbar.1": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "hotbar.2": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "hotbar.3": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "hotbar.4": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "hotbar.5": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "hotbar.6": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "hotbar.7": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "hotbar.8": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "hotbar.9": gym.spaces.Discrete(2),  # 0 or 1 (boolean)
                    "camera": gym.spaces.Box(
                        low=np.array([-180, -180]),
                        high=np.array([180, 180]),
                        dtype=np.float32,
                    ),
                    # Camera pitch/yaw between -180 and 180 degrees
                }
            )
        else:
            raise ValueError(f"Unknown action space version: {action_space_version}")
        entity_info_space = gym.spaces.Dict(
            {
                "unique_name": spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(1,),
                    dtype=np.int32,
                ),
                "translation_key": spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(1,),
                    dtype=np.int32,
                ),
                "x": spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(1,),
                    dtype=np.float64,
                ),
                "y": spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(1,),
                    dtype=np.float64,
                ),
                "z": spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(1,),
                    dtype=np.float64,
                ),
                "yaw": spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(1,),
                    dtype=np.float64,
                ),
                "pitch": spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(1,),
                    dtype=np.float64,
                ),
                "health": spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(1,),
                    dtype=np.float64,
                ),
            }
        )
        sound_entry_space = gym.spaces.Dict(
            {
                "translate_key": spaces.Box(
                    low=-np.inf, high=np.inf, shape=(1,), dtype=np.int32
                ),
                "x": spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float64),
                "y": spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float64),
                "z": spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float64),
                "age": spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.int32),
            }
        )
        entities_within_distance_space = gym.spaces.Sequence(entity_info_space)
        status_effect_space = gym.spaces.Dict(
            {
                "translation_key": spaces.Box(
                    low=-np.inf, high=np.inf, shape=(1,), dtype=np.int32
                ),
                "amplifier": spaces.Box(
                    low=-np.inf, high=np.inf, shape=(1,), dtype=np.int32
                ),
                "duration": spaces.Box(
                    low=-np.inf, high=np.inf, shape=(1,), dtype=np.int32
                ),
            }
        )
        self.observation_space = gym.spaces.Dict(
            {
                "obs": spaces.Dict(
                    {
                        "image": spaces.Box(
                            low=0,
                            high=255,
                            shape=(initial_env.imageSizeY, initial_env.imageSizeX, 3),
                            dtype=np.uint8,
                        ),
                        "position": spaces.Box(
                            low=-np.inf, high=np.inf, shape=(3,), dtype=np.float64
                        ),
                        "yaw": spaces.Box(
                            low=-np.inf, high=np.inf, shape=(1,), dtype=np.float64
                        ),
                        "pitch": spaces.Box(
                            low=-np.inf, high=np.inf, shape=(1,), dtype=np.float64
                        ),
                        "health": spaces.Box(
                            low=0, high=np.inf, shape=(1,), dtype=np.float64
                        ),
                        "food_level": spaces.Box(
                            low=0, high=np.inf, shape=(1,), dtype=np.float64
                        ),
                        "saturation_level": spaces.Box(
                            low=0, high=np.inf, shape=(1,), dtype=np.float64
                        ),
                        "is_dead": spaces.Discrete(2),
                        "inventory": spaces.Sequence(
                            spaces.Dict(
                                {
                                    "raw_id": spaces.Box(
                                        low=-np.inf,
                                        high=np.inf,
                                        shape=(1,),
                                        dtype=np.int32,
                                    ),
                                    "translation_key": spaces.Box(
                                        low=-np.inf,
                                        high=np.inf,
                                        shape=(1,),
                                        dtype=np.int32,
                                    ),
                                    "count": spaces.Box(
                                        low=-np.inf,
                                        high=np.inf,
                                        shape=(1,),
                                        dtype=np.int32,
                                    ),
                                    "durability": spaces.Box(
                                        low=-np.inf,
                                        high=np.inf,
                                        shape=(1,),
                                        dtype=np.int32,
                                    ),
                                    "max_durability": spaces.Box(
                                        low=-np.inf,
                                        high=np.inf,
                                        shape=(1,),
                                        dtype=np.int32,
                                    ),
                                }
                            ),
                        ),
                        "raycast_result": spaces.Dict(
                            {
                                "type": spaces.Discrete(3),
                                "target_block": spaces.Dict(
                                    {
                                        "x": spaces.Box(
                                            low=-np.inf,
                                            high=np.inf,
                                            shape=(1,),
                                            dtype=np.int32,
                                        ),
                                        "y": spaces.Box(
                                            low=-np.inf,
                                            high=np.inf,
                                            shape=(1,),
                                            dtype=np.int32,
                                        ),
                                        "z": spaces.Box(
                                            low=-np.inf,
                                            high=np.inf,
                                            shape=(1,),
                                            dtype=np.int32,
                                        ),
                                        "translation_key": spaces.Box(
                                            low=-np.inf,
                                            high=np.inf,
                                            shape=(1,),
                                            dtype=np.int32,
                                        ),
                                    }
                                ),
                                "target_entity": entity_info_space,
                            }
                        ),
                        "sound_subtitles": spaces.Sequence(sound_entry_space),
                        "status_effects": spaces.Sequence(status_effect_space),
                        "killed_statistics": spaces.Dict(),
                        "mined_statistics": spaces.Dict(),
                        "misc_statistics": spaces.Dict(),
                        "visible_entities": spaces.Sequence(entity_info_space),
                        "surrounding_entities": entities_within_distance_space,  # This is actually
                        "bobber_thrown": spaces.Discrete(2),
                        "experience": spaces.Box(
                            low=0, high=np.inf, shape=(1,), dtype=np.int32
                        ),
                        "world_time": spaces.Box(
                            low=-np.inf, high=np.inf, shape=(1,), dtype=np.int64
                        ),
                        "last_death_message": spaces.Text(
                            min_length=0, max_length=1000
                        ),
                        "image_2": spaces.Box(
                            low=0,
                            high=255,
                            shape=(initial_env.imageSizeY, initial_env.imageSizeX, 3),
                            dtype=np.uint8,
                        ),
                    }
                ),
            }
        )
        self.initial_env = initial_env
        self.use_terminate = use_terminate
        self.cleanup_world = cleanup_world
        self.use_vglrun = use_vglrun
        self.native_debug = native_debug
        self.track_native_memory = track_native_memory
        self.ld_preload = ld_preload
        self.encoding_mode = initial_env.screen_encoding_mode
        self.sock = None
        self.buffered_socket = None
        self.last_rgb_frames: List[Union[np.ndarray, torch.Tensor, None]] = [None, None]
        self.last_images: List[Union[np.ndarray, torch.Tensor, None]] = [None, None]
        self.last_action = None
        self.render_action = render_action
        self.verbose = verbose
        self.verbose_python = verbose_python
        self.verbose_gradle = verbose_gradle
        self.verbose_jvm = verbose_jvm
        self.profile = profile

        self.render_alternating_eyes = render_alternating_eyes
        self.render_alternating_eyes_counter = 0
        self.port = port
        self.find_free_port = find_free_port
        self.queued_commands = []
        self.process = None
        if env_path is None:
            self.env_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "MinecraftEnv",
            )
        else:
            self.env_path = env_path
        self.csv_logger = CsvLogger(
            "py_log.csv",
            profile=profile,
            backend=LogBackend.BOTH if verbose_python else LogBackend.NONE,
        )

        # in case when using zerocopy
        self.observation_tensors = [None, None]
        self.observation_tensor_type = ObservationTensorType.NONE

        if initial_env.screen_encoding_mode == ScreenEncodingMode.ZEROCOPY:
            try:
                from .craftground_native import initialize_from_mach_port  # type: ignore
                from .craftground_native import mtl_tensor_from_cuda_mem_handle  # type: ignore
            except ImportError:
                raise ImportError(
                    "To use zerocopy encoding mode, please install the craftground[cuda] package on linux or windows."
                    " If this error happens in macOS, please report it to the developers."
                )

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ) -> Tuple[ObsType, Dict[str, Any]]:
        if options is None:
            options = {}
        fast_reset = options.get("fast_reset", True)
        extra_commands = options.get("extra_commands", [])
        if not self.sock:  # first time
            self.start_server(
                port=self.port,
                use_vglrun=self.use_vglrun,
                track_native_memory=self.track_native_memory,
                ld_preload=self.ld_preload,
            )
        else:
            if not fast_reset:
                self.sock.close()
                self.terminate()
                # wait for server death and restart server
                sleep(5)
                self.start_server(
                    port=self.port,
                    use_vglrun=self.use_vglrun,
                    track_native_memory=self.track_native_memory,
                    ld_preload=self.ld_preload,
                )
            else:
                self.csv_logger.profile_start("fast_reset")
                send_fastreset2(self.sock, extra_commands)
                self.csv_logger.profile_end("fast_reset")
                self.csv_logger.log("Sent fast reset")
                if self.verbose_python:
                    print_with_time("Sent fast reset")
        self.csv_logger.log("Reading response...")
        self.csv_logger.profile_start("read_response")
        siz, res = self.read_one_observation()
        self.csv_logger.profile_end("read_response")

        self.csv_logger.log(f"Got response with size {siz}")
        self.csv_logger.profile_start("convert_observation")
        rgb_1, img_1 = self.convert_observation(res.image, res)
        self.csv_logger.profile_end("convert_observation")
        rgb_2 = None
        img_2 = None
        if res.image_2 is not None and res.image_2 != b"":
            rgb_2, img_2 = self.convert_observation(res.image_2, res)
        self.queued_commands = []
        res.yaw = ((res.yaw + 180) % 360) - 180
        final_obs: Dict[str, Union[np.ndarray, torch.Tensor, Any]] = {
            "obs": res,
            "rgb": rgb_1,
        }
        self.last_images = [img_1, img_2]
        self.last_rgb_frames = [rgb_1, rgb_2]
        if rgb_2 is not None:
            final_obs["rgb_2"] = rgb_2
        return final_obs, final_obs

    """
    returns:
    - numpy array or torch Tensor of the image
    - PIL image (optional)
    - numpy array of the last_rgb_frame
    """

    def convert_observation(
        self, image_bytes: bytes, res: ObsType
    ) -> Tuple[Union[np.ndarray, torch.Tensor], Optional[Image.Image]]:
        if self.encoding_mode == ScreenEncodingMode.PNG:
            # decode png byte array to numpy array
            # Create a BytesIO object from the byte array
            self.csv_logger.profile_start("convert_observation/decode_png")
            bytes_io = io.BytesIO(image_bytes)
            # Use PIL to open the image from the BytesIO object
            img = Image.open(bytes_io).convert("RGB")
            # Flip y axis
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            self.csv_logger.profile_end("convert_observation/decode_png")
            self.csv_logger.profile_start("convert_observation/convert_to_numpy")
            # Convert the PIL image to a numpy array
            last_rgb_frame = np.array(img)
            arr = np.transpose(last_rgb_frame, (2, 1, 0))
            rgb_array_or_tensor = arr.astype(np.uint8)
            self.csv_logger.profile_end("convert_observation/convert_to_numpy")
        elif self.encoding_mode == ScreenEncodingMode.RAW:
            # decode raw byte array to numpy array
            self.csv_logger.profile_start("convert_observation/decode_raw")
            last_rgb_frame = np.frombuffer(image_bytes, dtype=np.uint8).reshape(
                (self.initial_env.imageSizeY, self.initial_env.imageSizeX, 3)
            )
            # Flip y axis using np
            # last_rgb_frame = np.transpose(last_rgb_frame, (1, 0, 2))
            last_rgb_frame = np.flip(last_rgb_frame, axis=0)
            rgb_array_or_tensor = last_rgb_frame
            # arr = np.transpose(last_rgb_frame, (2, 1, 0))  # channels, width, height
            img = None
            self.csv_logger.profile_end("convert_observation/decode_raw")
        elif self.encoding_mode == ScreenEncodingMode.ZEROCOPY:
            import torch

            if self.initial_env.eye_distance > 0:  # binocular vision
                # TODO: Handle binocular vision
                if (
                    self.observation_tensors[0] is not None
                    and self.observation_tensors[1] is not None
                ):
                    # already intialized
                    # drop alpha, flip y axis, and clone
                    if (
                        self.observation_tensor_type
                        == ObservationTensorType.APPLE_TENSOR
                    ):
                        return (
                            self.observation_tensors[0]
                            .clone()[:, :, [2, 1, 0]]
                            .flip(0),
                            None,
                        )
                    elif (
                        self.observation_tensor_type
                        == ObservationTensorType.CUDA_DLPACK
                    ):
                        return (
                            self.observation_tensors[0].clone()[:, :, :3].flip(0),
                            None,
                        )
            else:
                if self.observation_tensors[0] is not None:
                    # already intialized
                    # drop alpha, flip y axis, and clone
                    if (
                        self.observation_tensor_type
                        == ObservationTensorType.APPLE_TENSOR
                    ):
                        return (
                            self.observation_tensors[0]
                            .clone()[:, :, [2, 1, 0]]
                            .flip(0),
                            None,
                        )
                    elif (
                        self.observation_tensor_type
                        == ObservationTensorType.CUDA_DLPACK
                    ):
                        return (
                            self.observation_tensors[0].clone()[:, :, :3].flip(0),
                            None,
                        )

            from .craftground_native import initialize_from_mach_port  # type: ignore
            from .craftground_native import mtl_tensor_from_cuda_mem_handle  # type: ignore

            if len(res.ipc_handle) == 0:
                raise ValueError("No ipc handle found.")
            if len(res.ipc_handle) == 4:
                mach_port = int.from_bytes(
                    res.ipc_handle, byteorder="little", signed=False
                )
                print(f"{mach_port=}")
                apple_dl_tensor = initialize_from_mach_port(
                    mach_port, self.initial_env.imageSizeX, self.initial_env.imageSizeY
                )
                if apple_dl_tensor is not None:
                    # image_tensor = torch.utils.dlpack.from_dlpack(apple_dl_tensor)
                    rgb_array_or_tensor = apple_dl_tensor
                    print(rgb_array_or_tensor.shape)
                    print(rgb_array_or_tensor.dtype)
                    print(rgb_array_or_tensor.device)
                    self.observation_tensors[0] = rgb_array_or_tensor
                    # drop alpha, flip y axis, and clone
                    rgb_array_or_tensor = rgb_array_or_tensor.clone()[
                        :, :, [2, 1, 0]
                    ].flip(0)
                    self.observation_tensor_type = ObservationTensorType.APPLE_TENSOR
                else:
                    raise ValueError(
                        f"Failed to initialize from mach port {res.ipc_handle}."
                    )
            else:
                import torch.utils.dlpack

                cuda_dl_tensor = mtl_tensor_from_cuda_mem_handle(
                    res.ipc_handle,
                    self.initial_env.imageSizeX,
                    self.initial_env.imageSizeY,
                )
                if not cuda_dl_tensor:
                    raise ValueError("Invalid DLPack capsule: None")
                rgb_array_or_tensor = torch.utils.dlpack.from_dlpack(cuda_dl_tensor)
                print(rgb_array_or_tensor.shape)
                print(rgb_array_or_tensor.dtype)
                print(rgb_array_or_tensor.device)
                print(f"{rgb_array_or_tensor.data_ptr()=}\n\n")
                self.observation_tensors[0] = rgb_array_or_tensor
                # drop alpha, flip y axis, and clone
                rgb_array_or_tensor = (
                    self.observation_tensors[0].clone()[:, :, :3].flip(0)
                )
                self.observation_tensor_type = ObservationTensorType.CUDA_DLPACK
            img = None

        else:
            raise ValueError(f"Unknown encoding mode: {self.encoding_mode}")
        return rgb_array_or_tensor, img

    def start_server(
        self,
        port: int,
        use_vglrun: bool,
        track_native_memory: bool,
        ld_preload: Optional[str],
    ):
        self.remove_orphan_java_processes()
        # Check if a file exists
        if os.name == "nt":
            while True:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex(("127.0.0.1", port)) == 0:  # The port is in use
                        if self.find_free_port:
                            print(
                                f"[Warning]: Port {port} is already in use. Trying another port."
                            )
                            port += 1
                        else:
                            raise ConnectionError(
                                f"Port {port} is already in use. Please choose another port."
                            )
                    else:
                        break
        else:
            socket_path = f"/tmp/minecraftrl_{port}.sock"
            if os.path.exists(socket_path):
                if self.find_free_port:
                    print(
                        f"[Warning]: Socket file {socket_path} already exists. Trying another port."
                    )
                    while os.path.exists(socket_path):
                        port += 1
                        socket_path = f"/tmp/minecraftrl_{port}.sock"
                    print(f"Using port {socket_path}")
                else:
                    raise FileExistsError(
                        f"Socket file {socket_path} already exists. Please choose another port."
                    )
        my_env = os.environ.copy()
        my_env["PORT"] = str(port)
        my_env["VERBOSE"] = str(int(self.verbose_jvm))
        if track_native_memory:
            my_env["CRAFTGROUND_JVM_NATIVE_TRACKING"] = "detail"
        if self.native_debug:
            my_env["CRAFGROUND_NATIVE_DEBUG"] = "True"
        # configure permission of the gradlew
        gradlew_path = os.path.join(self.env_path, "gradlew")
        if not os.access(gradlew_path, os.X_OK):
            os.chmod(gradlew_path, 0o755)
        # update image settings of options.txt if exists
        options_txt_path = self.get_env_option_path()
        if options_txt_path is not None:
            if os.path.exists(options_txt_path):
                pass
                # self.update_override_resolutions(options_txt_path)

        if os.name == "nt":
            cmd = f".\\gradlew runClient -w --no-daemon"
        else:
            cmd = f"./gradlew runClient -w --no-daemon"  #  --args="--width {self.initial_env.imageSizeX} --height {self.initial_env.imageSizeY}"'
        if use_vglrun:
            cmd = f"vglrun {cmd}"
        if ld_preload:
            my_env["LD_PRELOAD"] = ld_preload
        print(f"{cmd=}")
        self.process = subprocess.Popen(
            cmd,
            cwd=self.env_path,
            shell=True,
            stdout=subprocess.DEVNULL if not self.verbose_gradle else None,
            env=my_env,
        )
        sock: socket.socket = wait_for_server(port)
        self.sock = sock
        self.send_initial_env()
        self.buffered_socket = BufferedSocket(self.sock)
        # self.json_socket.send_json_as_base64(self.initial_env.to_dict())
        if self.verbose_python:
            print_with_time("Sent initial environment")
        self.csv_logger.log("Sent initial environment")

    def update_override_resolutions(self, options_txt_path):
        with open(options_txt_path, "r") as file:
            text = file.read()

            # Define the patterns for overrideWidth and overrideHeight
        width_pattern = r"overrideWidth:\d+"
        height_pattern = r"overrideHeight:\d+"

        # Update or add overrideWidth
        if re.search(width_pattern, text):
            text = re.sub(
                width_pattern, f"overrideWidth:{self.initial_env.imageSizeX}", text
            )
        else:
            text += f"\noverrideWidth:{self.initial_env.imageSizeX}"

        # Update or add overrideHeight
        if re.search(height_pattern, text):
            text = re.sub(
                height_pattern, f"overrideHeight:{self.initial_env.imageSizeY}", text
            )
        else:
            text += f"\noverrideHeight:{self.initial_env.imageSizeY}"

        # Write the updated text back to the file
        with open(options_txt_path, "w") as file:
            file.write(text)
        print(
            f"Updated {options_txt_path} to {self.initial_env.imageSizeX}x{self.initial_env.imageSizeY}"
        )

    def read_one_observation(self) -> Tuple[int, ObsType]:
        # print("Reading observation size...")
        data_len_bytes = self.buffered_socket.read(4, True)
        # print("Reading observation...")
        data_len = struct.unpack("<I", data_len_bytes)[0]
        data_bytes = self.buffered_socket.read(data_len, True)
        observation_space = observation_space_pb2.ObservationSpaceMessage()
        # print("Parsing observation...")
        observation_space.ParseFromString(data_bytes)
        # print("Parsed observation...")
        return data_len, observation_space

    def send_initial_env(self):
        initial_env = self.initial_env.to_initial_environment_message()
        # print(
        #     "Sending initial environment... ",
        # )
        v = initial_env.SerializeToString()
        # print(base64.b64encode(v).decode())
        self.sock.send(struct.pack("<I", len(v)))
        self.sock.sendall(v)

    def translate_action_to_v2(self, action: ActType) -> Dict[str, Union[bool, float]]:
        translated_action = {
            "attack": action[5] == 3,
            "back": action[0] == 2,
            "forward": action[0] == 1,
            "jump": action[2] == 1,
            "left": action[1] == 1,
            "right": action[1] == 2,
            "sneak": action[2] == 2,
            "sprint": action[2] == 3,
            "use": action[5] == 1,
            "drop": action[5] == 2,
            "inventory": False,
        }
        for i in range(1, 10):
            translated_action[f"hotbar.{i}"] = False

        translated_action["camera_pitch"] = action[3] * 15 - 180.0
        translated_action["camera_yaw"] = action[4] * 15 - 180.0

        return translated_action

    def step(self, action: ActType) -> Tuple[ObsType, float, bool, bool, dict]:
        # send the action
        self.last_action = action
        self.csv_logger.profile_start("send_action_and_commands")
        # Translate the action v1 to v2
        if self.action_space_version == ActionSpaceVersion.V1_MINEDOJO:
            translated_action = self.translate_action_to_v2(action)
        else:
            translated_action = action
        send_action_and_commands(
            self.sock,
            translated_action,
            commands=self.queued_commands,
            verbose=self.verbose_python,
        )
        self.csv_logger.profile_end("send_action_and_commands")
        self.queued_commands.clear()
        # read the response
        if self.verbose_python:
            print_with_time("Sent action and reading response...")
        self.csv_logger.log("Sent action and reading response...")
        self.csv_logger.profile_start("read_response")
        siz, res = self.read_one_observation()
        self.csv_logger.profile_end("read_response")
        if self.verbose_python:
            print_with_time("Read observation...")
        self.csv_logger.log("Read observation...")
        self.csv_logger.profile_start("convert_observation")
        rgb_1, img_1 = self.convert_observation(res.image, res)
        self.csv_logger.profile_end("convert_observation")
        rgb_2 = None
        img_2 = None
        frame_2 = None
        if res.image_2 is not None and res.image_2 != b"":
            rgb_2, img_2 = self.convert_observation(res.image_2, res)
        final_obs = {
            "obs": res,
            "rgb": rgb_1,
        }
        res.yaw = ((res.yaw + 180) % 360) - 180
        self.last_images = [img_1, img_2]
        self.last_rgb_frames = [rgb_1, rgb_2]
        if rgb_2 is not None:
            final_obs["rgb_2"] = rgb_2

        reward = 0  # Initialize reward to zero
        done = False  # Initialize done flag to False
        truncated = False  # Initialize truncated flag to False
        return (
            final_obs,
            reward,
            done,
            truncated,
            final_obs,
        )

    # when self.render_mode is None: no render is computed
    # when self.render_mode is "human": render returns None, envrionment is already being rendered on the screen
    # when self.render_mode is "rgb_array": render returns the image to be rendered
    # when self.render_mode is "ansi": render returns the text to be rendered
    # when self.render_mode is "rgb_array_list": render returns a list of images to be rendered
    # when self.render_mode is "rgb_tensor": render returns a torch tensor to be rendered
    def render(self) -> Union[RenderFrame, List[RenderFrame], None]:
        # print("Rendering...")
        # select last_image and last_frame
        if self.render_mode is None:
            return None
        if self.render_mode == "human":
            # do not render anything
            return None
        if self.render_mode == "ansi":
            raise ValueError("Rendering mode ansi not supported")
        if self.render_mode == "rgb_array_list":
            raise ValueError("Rendering mode rgb_array_list not supported")

        if self.render_alternating_eyes:
            last_image = self.last_images[self.render_alternating_eyes_counter]
            last_rgb_frame = self.last_rgb_frames[self.render_alternating_eyes_counter]
            self.render_alternating_eyes_counter = (
                1 - self.render_alternating_eyes_counter
            )
        else:
            last_image = self.last_images[0]
            last_rgb_frame = self.last_rgb_frames[0]
        if last_image is None and last_rgb_frame is None:
            return None

        if isinstance(last_rgb_frame, torch.Tensor) and (
            self.render_mode != "rgb_array_tensor" or self.render_action
        ):
            # drop the alpha channel and convert to numpy array
            last_rgb_frame = last_rgb_frame.cpu().numpy()
        # last_rgb_frame: np.ndarray or torch.Tensor
        # last_image: PIL.Image.Image or None
        if self.render_action and self.last_action:
            if last_image is None:
                # it is inevitable to convert the tensor to numpy array
                last_image = Image.fromarray(last_rgb_frame)
            self.csv_logger.profile_start("render_action")
            draw = ImageDraw.Draw(last_image)
            if self.action_space_version == ActionSpaceVersion.V1_MINEDOJO:
                text = self.action_to_symbol(self.last_action)
            elif self.action_space_version == ActionSpaceVersion.V2_MINERL_HUMAN:
                text = self.action_v2_to_symbol(self.last_action)
            else:
                raise ValueError(
                    f"Unknown action space version {self.action_space_version}"
                )
            position = (0, 0)
            font = get_font()
            font_size = 8
            color = (255, 0, 0)
            draw.text(position, text, font=font, font_size=font_size, fill=color)
            self.csv_logger.profile_end("render_action")
            return np.array(last_image)
        else:
            return last_rgb_frame

    def action_to_symbol(self, action) -> str:  # noqa: C901
        res = ""
        if action[0] == 1:
            res += "↑"
        elif action[0] == 2:
            res += "↓"
        if action[1] == 1:
            res += "←"
        elif action[1] == 2:
            res += "→"
        if action[2] == 1:
            res += "jump"  # "⤴"
        elif action[2] == 2:
            res += "sneak"  # "⤵"
        elif action[2] == 3:
            res += "sprint"  # "⚡"
        if action[3] > 12:  # pitch up
            res += "⤒"
        elif action[3] < 12:  # pitch down
            res += "⤓"
        if action[4] > 12:  # yaw right
            res += "⏭"
        elif action[4] < 12:  # yaw left
            res += "⏮"
        if action[5] == 1:  # use
            res += "use"  # "⚒"
        elif action[5] == 2:  # drop
            res += "drop"  # "🤮"
        elif action[5] == 3:  # attack
            res += "attack"  # "⚔"
        return res

    def action_v2_to_symbol(  # noqa: C901
        self, action_v2: Dict[str, Union[int, float]]
    ) -> str:
        res = ""

        if action_v2.get("forward") == 1:
            res += "↑"
        if action_v2.get("backward") == 1:
            res += "↓"
        if action_v2.get("left") == 1:
            res += "←"
        if action_v2.get("right") == 1:
            res += "→"
        if action_v2.get("jump") == 1:
            res += "JMP"
        if action_v2.get("sneak") == 1:
            res += "SNK"
        if action_v2.get("sprint") == 1:
            res += "SPRT"
        if action_v2.get("attack") == 1:
            res += "ATK"
        if action_v2.get("use") == 1:
            res += "USE"
        if action_v2.get("drop") == 1:
            res += "Q"
        if action_v2.get("inventory") == 1:
            res += "I"

        for i in range(1, 10):
            if action_v2.get(f"hotbar.{i}") == 1:
                res += f"hotbar.{i}"

        return res

    @property
    def render_mode(self) -> Optional[str]:
        return "rgb_array"

    def close(self):
        if not self.use_terminate:
            self.terminate()
        else:
            print("Not terminating the java process")

    def add_command(self, command: str):
        self.queued_commands.append(command)

    def add_commands(self, commands: List[str]):
        self.queued_commands.extend(commands)

    def terminate(self):
        if self.sock is not None:
            send_exit(self.sock)
            self.sock.close()
            self.sock = None
        print("Terminated the java process")
        pid = self.process.pid if self.process else None
        # wait for the pid to exit
        try:
            if pid:
                os.kill(pid, signal.SIGKILL)
                _, exit_status = os.waitpid(pid, 0)
            else:
                print("No pid to wait for")
        except ChildProcessError:
            print("Child process already terminated")
        print("Terminated the java process")

    def remove_orphan_java_processes(self):  # noqa: C901
        print("Removing orphan Java processes...")
        target_directory = "/tmp"
        file_pattern = "minecraftrl_"
        file_usage = {}
        no_such_processes = 0
        access_denied_processes = 0
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                for file in proc.open_files():
                    if (
                        file.path.startswith(target_directory)
                        and file_pattern in file.path
                    ):
                        if file.path not in file_usage:
                            file_usage[file.path] = []
                        file_usage[file.path].append(proc.info)
            except psutil.NoSuchProcess:
                no_such_processes += 1
                continue
            except psutil.AccessDenied:
                access_denied_processes += 1
                continue
            except Exception as e:
                print(f"Error: {e}")
                continue

        for file_path, processes in file_usage.items():
            if all(proc["name"].lower() == "java" for proc in processes):
                for proc in processes:
                    os.kill(proc["pid"], signal.SIGTERM)
                    print(f"Killed Java process {proc['pid']} using file {file_path}")
                os.remove(file_path)
                print(f"Removed {file_path}")
        print(
            f"Removed orphan Java processes: {access_denied_processes} access denied, {no_such_processes} no such process"
        )

    # Copy or symlink the save file to the returned folder
    @staticmethod
    def get_env_save_path() -> str:
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        env_dir = os.path.join(current_dir, "MinecraftEnv", "run", "saves")
        return env_dir

    @staticmethod
    def get_env_option_path() -> str:
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        options_txt = os.path.join(current_dir, "MinecraftEnv", "run", "options.txt")
        return options_txt
