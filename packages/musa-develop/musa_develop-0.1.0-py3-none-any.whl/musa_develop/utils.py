import subprocess
import platform
import os
import re
import tarfile
import zipfile
import sys
import requests
from datetime import datetime
from tqdm import tqdm
from typing import Union

GPU_ARCH_MAP = {
    "0111": "mp_10",
    "0106": "mp_10",
    "0105": "mp_10",
    "0102": "mp_10",
    "0101": "mp_10",
    "0100": "mp_10",
    "0123": "mp_10",
    "0122": "mp_10",
    "0121": "mp_10",
    "0201": "mp_21",
    "0200": "mp_21",
    "0222": "mp_21",
    "0203": "mp_21",
    "0202": "mp_21",
    "0301": "mp_22",
    "0300": "mp_22",
    "0323": "mp_22",
    "0327": "mp_22",
}

GPU_TYPE_MAP = {
    "0323": "S4000",
    "0301": "S90",
    "0222": "S3000",
    "0201": "S80",
    "0200": "S80",
    "0202": "S70",
}

GPU_MEMORY_MAP = {
    "MTT S70": 7168,
    "MTT S80": 16384,
    "MTT S90": 24576,
    "MTT S3000": 32768,
    "MTT S4000": 49152,
    "MTT S5000": 81920,
}

MUSA_BIN_PATH = "/usr/local/musa/bin"
MUSA_LIB_PATH = "/usr/local/musa/lib"


def FontGreen(string: str):
    return "\033[32m" + string + "\033[0m"


def FontRed(string: str):
    return "\033[91m" + string + "\033[0m"


def parse_args(args):
    pattern = re.compile(r"([a-zA-Z0-9_]+)(==|=|--|-)?(.*)")
    match = pattern.match(args)
    if match:
        name = match.group(1)
        version = match.group(3).strip() if match.group(3) else None
        return name, version
    else:
        raise ValueError(f"Invalid input format: {args}")


def demo_parse_args(args):
    pattern = re.compile(r"([a-zA-Z0-9_]+)(==|=|--|-)([0-9.]+)(==|=|--|-)(docker)?")
    match = pattern.match(args)
    if match:
        name = match.group(1)
        version = match.group(3)
        is_docker = bool(match.group(5))
        return name, version, is_docker
    else:
        pattern = re.compile(r"([a-zA-Z0-9_]+)(==|=|--|-)?(.*)")
        match = pattern.match(args)
        if match:
            name = match.group(1)
            kargs = match.group(3).strip() if match.group(3) else None
            if not kargs:
                return name, None, False
            elif "docker" == kargs:
                return name, None, True
            else:
                return name, kargs, False
        else:
            raise ValueError(f"Invalid input format: {args}")


def require_root_privileges_check():
    if os.geteuid() != 0:
        print(
            FontRed(
                "This process must be ran with 'root' or 'sudo' privileges, but now it is not!"
            )
        )
        exit()


def ping(url):
    # 参数解析：'-n' 表示发送的echo请求的次数，'-w' 表示等待回复的超时时间（毫秒）
    # 这些参数在不同的操作系统中可能有所不同，这里以Windows为例
    parameter = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", parameter, "1", url]  # 对URL执行一次ping操作

    try:
        response = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        # ping命令执行成功，返回码为0
        if response.returncode == 0:
            print(f"Ping {url} successful")
            return True
        else:
            print(f"Ping {url} failed")
            return False
    except Exception as e:
        print(f"Error pinging {url}: {e}")
        return False


def FormatGitVersion(version: str = None):
    split_version = version.split("+")
    return (
        split_version[0] + "+" + split_version[1][0:7]
        if len(split_version) == 2
        else version
    )


class SHELL:
    def __init__(self, shell=True, text_mode=True):
        self.shell = shell
        self.text_mode = text_mode

    def run_cmd(self, cmd: str, is_split=True):
        completed_process = subprocess.run(
            cmd,
            shell=self.shell,
            text=self.text_mode,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        # Flexible control of whether to preprocess the original output
        if is_split:
            completed_process.stdout = self.check_output(completed_process.stdout)
        return (
            completed_process.stdout,
            completed_process.stderr,
            completed_process.returncode,
        )

    def run_cmd_with_error_print(self, cmd: str):
        try:
            subprocess.run(
                cmd, shell=True, check=True, stderr=subprocess.PIPE, text=True
            )
        except subprocess.CalledProcessError as e:
            print(e.stderr, file=sys.stderr, end="")

    def check_output(self, output) -> list:
        """
        If the output is a string with newline characters, split it into a list
        """
        if isinstance(output, str):
            output = output.strip()
            if "\n" in output:
                return [line.strip() for line in output.splitlines()]
            else:
                return output
        else:
            return output


def download_file_with_progress(url, save_path):
    if os.path.exists(save_path):
        print(f"File was saved at {save_path}.")
        return
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(
            f"Failed to download file from {url}. HTTP status code: {response.status_code}"
        )
        return
    total_size = int(response.headers.get("content-length", 0))
    progress_bar = tqdm(
        total=total_size, unit="B", unit_scale=True, desc=os.path.basename(save_path)
    )
    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                file.write(chunk)
                progress_bar.update(len(chunk))
    progress_bar.close()
    if total_size != 0 and progress_bar.n != total_size:
        print(f"Files from {url} was downloaded incompletely, please try it again!")
    else:
        print(f"File downloaded successfully: {save_path}")


def generate_name_with_time(prefix: str = None):
    date_time = datetime.now()
    timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
    name = f"{prefix}_{timestamp}"
    return name


class BaseDecompressor:
    def __init__(self):
        pass

    def create_output_dir(self, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            return output_dir

    def extract_tar_gz(self, archive_path, output_dir):
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(output_dir)

    def extract_zip(self, archive_path, output_dir):
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)


def get_gpu_type():
    gmi_infos = SHELL().run_cmd("mthreads-gmi -q")[0]
    lspci_infos = SHELL().run_cmd("lspci -n | grep 1ed5")
    if gmi_infos:
        for value in gmi_infos:
            if "Device ID" in value:
                val = value.split(":")[-1].strip()
                return GPU_ARCH_MAP[val[2:]]
    if lspci_infos:
        key_arch = lspci_infos[0][0].split(":")[-1]
        return GPU_ARCH_MAP[key_arch]
    return GPU_ARCH_MAP["0323"]


def convert_underline_to_hyphen(
    name: Union[str, list], reverse=False
) -> Union[str, list]:
    """
    Converts underscores to hyphens or hyphens to underscores in a given string or list of strings.

    Parameters:
        name (Union[str, List[str]]): The input string or list of strings to be converted.
        reverse (bool): If True, converts hyphens to underscores.
                        If False (default), converts underscores to hyphens.

    Returns:
        Union[str, List[str]]: The converted string or list of strings with the changes applied.
    """

    if isinstance(name, str):
        if reverse:
            return name.replace("-", "_")
        else:
            return name.replace("_", "-")
    else:
        return [convert_underline_to_hyphen(item, reverse) for item in name]


REPORT_TITLE = """\
=====================================================================
======================= MOORE THREADS REPORT ========================
====================================================================="""

CHECK_TITLE = """\
=====================================================================
======================== MOORE THREADS CHECK ========================
====================================================================="""

REPORT_END_LINE = """\
====================================================================="""

SEPARATION_LINE = """\
---------------------------------------------------------------------"""


def GenerateContainerName(demo: str, task: str, prefix: str = "musa_develop") -> str:
    """Generate a container name based on the current timestamp

    Args:
        task (str): Task will be run by DEMO module.
        prefix (str, optional): Defaults to "musa-develop".

     Returns:
        str: A unique container name.
    """
    date_time = datetime.now()
    timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
    return f"{prefix}_{demo}_{task}_{timestamp}"
