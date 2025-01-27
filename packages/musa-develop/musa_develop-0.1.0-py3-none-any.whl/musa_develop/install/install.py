import os
import re
from abc import ABC, abstractmethod
from typing import Literal


from musa_develop.check import CHECKER
from musa_develop.check.utils import (
    CheckModuleNames,
    MusaModule,
    ContainerToolkitModule,
    EXECUTED_ON_HOST_FLAG,
)
from musa_develop.download import DOWNLOADER
from musa_develop.utils import (
    SHELL,
    MUSA_BIN_PATH,
    MUSA_LIB_PATH,
    FontGreen,
    FontRed,
    BaseDecompressor,
    require_root_privileges_check,
    generate_name_with_time,
)


CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
CURRENT_WORK_DIR = os.getcwd()


class DownloadDecompressor(BaseDecompressor):

    def __init__(self, archive_dict: dict):
        super().__init__()
        self._archive_dict = archive_dict
        self._decompress_dict = dict()

    def create_dir_and_extract(self, archive_path: str) -> str:
        # 1. create output dir base on archive file name
        if os.path.isfile(archive_path) and re.search(
            r"\.(tar\.gz|tar|zip)$", archive_path, re.IGNORECASE
        ):
            to_create_dir = generate_name_with_time(
                re.sub(
                    r"\.tar\.gz$|\.zip|\.tar$", "", archive_path, flags=re.IGNORECASE
                )
            )  # 去掉后缀并创建输出目录
            output_dir = self.create_output_dir(to_create_dir)
        else:
            return archive_path
        # 2. extract content to output_dir
        if archive_path.endswith(".tar.gz"):
            self.extract_tar_gz(archive_path, output_dir)
        elif archive_path.endswith(".zip"):
            self.extract_zip(archive_path, output_dir)
        else:
            raise ValueError(
                f"Unsupported archive format: '{archive_path}'. "
                "Supported formats are '.tar.gz' and '.zip'. "
                f"Please check the file path and ensure it uses a valid archive format."
            )
        return output_dir

    def extract_container_toolkit(self, tag: str, archive: str):
        """
        get mt-container-toolkit, mtml, sgpu-dkms deb path

        Attention:
        self.archive_path: /xxx/mt-container-toolkit-x.x.x.zip

        Returns:
            dict: A dictionary containing the paths to the downloaded files, eg:
            {
                "mtml": "/xxx/mtml_x.x.x.deb",
                "sgpu-dkms": "/xxx/sgpu-dkms_x.x.x.deb",
                "container-toolkit": "/xxx/mt-container-toolkit-x.x.x.deb"
            }
        """
        packages_path_dict = {}
        # 1. create output_dir and extract archive to output_dir
        output_dir = self.create_dir_and_extract(archive)
        # 2. get deb path in output_dir by regex
        deb_pattern = re.compile(
            rf"(.*)({ContainerToolkitModule.mtml.name}|{ContainerToolkitModule.sgpu_dkms.name.replace('_', '-')}|{ContainerToolkitModule.container_toolkit.name.replace('_', '-')})(.*\.deb)$",
            re.IGNORECASE,
        )
        for file_path in os.listdir(output_dir):
            match = deb_pattern.search(file_path)
            if match:
                # if matched, return path, key is package name
                packages_path_dict[match.group(2)] = os.path.join(output_dir, file_path)

        self._decompress_dict.update(packages_path_dict)

    def extract_musa_single_component(
        self, tag: str, archive: str, target_filename_part="install"
    ):
        """
        get install.sh path for musa_toolkits, mudnn or mccl

        Args:
            component_name (str): The name of the component to extract information for, eg: musa_toolkits, mudnn, mccl, etc.
            target_filename_part (str): The part of the filename to search for, eg: install_mudnn.sh
        """
        pattern = re.compile(
            r"""
            .*         #
            install    # filename contain str: "install"
            .*
            \.sh$      # end with .sh
            """,
            re.IGNORECASE | re.VERBOSE,
        )
        packages_path_dict = {}
        output_dir = self.create_dir_and_extract(archive)
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if pattern.match(file):
                    packages_path_dict[tag] = os.path.join(root, file)
                    break
        self._decompress_dict.update(packages_path_dict)

    def extract_sdk_components(self, tag: str, archive: str):
        """
        get mccl, mudnn, musa_toolkits, driver, smartio file path

        Attention:
            We assume mccl, mudnn, and musa_toolkit file path are compressed packages, while the others are .deb packages.
        """
        packages_path_dict = {}
        output_dir = self.create_dir_and_extract(archive)
        # TODO(@caizhi): 取名不统一(musa_toolkits, smartio)
        pattern = re.compile(
            r"""
            .*         # Match the general part of the path
            (?P<keyword>  # Capture the keyword group
            mccl                                    |  # Match "mccl"
            mudnn                                   |  # Match "mudnn"
            musa_toolkits                           |  # Match "musa_toolkits"
            driver                                  |  # Match "driver"
            smartio                                 # Match "smartio"
            )
            .*
            \.         # Match the period before the file extension
            (tar\.gz|deb|zip|tar)$  # Match supported file extensions
            """,
            re.IGNORECASE | re.VERBOSE,
        )
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                match = pattern.match(file_path)
                if match:
                    # get mccl, mudnn, musa_toolkits, driver, smartio file path
                    # mccl, mudnn, musa_toolkits is .tar.gz file
                    packages_path_dict[match.group("keyword").lower()] = file_path
        self._decompress_dict.update(packages_path_dict)
        self.extract_musa_single_component(self._decompress_dict["musa_toolkits"])
        self.extract_musa_single_component(self._decompress_dict[MusaModule.mudnn.name])
        self.extract_musa_single_component(self._decompress_dict[MusaModule.mccl.name])

    def decompress(self):
        for key, value in self._archive_dict.items():
            if "container_toolkit" in key:
                self.extract_container_toolkit(key, value)
            elif "sdk" in key:
                self.extract_sdk_components(key, value)
            elif "musa_toolkits" in key or "mudnn" in key or "mccl" in key:
                self.extract_musa_single_component(key, value)
            else:
                self._decompress_dict[key] = value
        return self._decompress_dict


class PackageManager(ABC):

    def __init__(self):
        self._name = None
        self._checker = None
        self._preinstaller = list()
        self._target_package_name = None  # 目标包名
        self._dependency_package_list = []  # 依赖包列表
        self._shell = SHELL()
        self._version = None
        self._pkg_path_dict = dict()
        self._driver_version = None  # Driver version is always a key element
        # TODO(@caizhi): need store all recommendation
        self._last_recommendation = list()
        self._is_installed_file_flag = (
            None  # using for verify after uninstall by sh script
        )
        # =========
        # need check name

    def update_version(self, version: str = None):
        self._target_version = version

    @abstractmethod
    def uninstall_cmd(self):
        # TODO(@wangkang): torch_musa存在需要多次卸载的情况
        pass

    def verify_is_installed(
        self,
        package_name: str,
        is_installed_file_flag: str,
        package_type: Literal["dpkg", "pip", "apt", "sh"],
    ) -> bool:
        """
         Verifies whether a package or directory is installed or exists based on its type.

        Args:
            package_name_or_dir (str):
                The name of the package (for dpkg, pip, or apt) or the directory path (for sh).
            package_type (Literal["dpkg", "pip", "apt", "sh"]):
                The type of the package or check method:
                - "dpkg": if the package is managed by dpkg.
                - "pip": if the package is managed by pip.
                - "apt": if the package is managed by apt.
                - "sh": if the directory exists(package is installed via the sh script).

        Returns:
            bool: True if the package or directory is installed or exists, False otherwise.

        """
        if package_type in ["dpkg", "apt"]:
            stdout, _, _ = self._shell.run_cmd(f"dpkg -s {package_name}")
        elif package_type == "pip":
            stdout, _, _ = self._shell.run_cmd(
                f"pip show {package_name}"
            )  # pip show package_name
        elif package_type == "sh":
            stdout, _, _ = self._shell.run_cmd(
                f"test -e {package_name}"
            )  # test -e path

        return bool(stdout)

    def uninstall(self):
        # uninstall
        self.uninstall_cmd()
        # verify
        uninstall_package_list = [
            self._target_package_name,
            *self._dependency_package_list,
        ]
        for package_name in uninstall_package_list:
            is_installed_bool = self.verify_is_installed(
                package_name=self._target_package_name,
                package_type=self._package_type,
                is_installed_file_flag=self._is_installed_file_flag,
            )
            if is_installed_bool:
                print(
                    f"Warning: The package {package_name} is not uninstalled successfully!"
                )
            else:
                if self._name == CheckModuleNames.driver.name:
                    print(f"Successfully uninstall {FontRed(f'{self._name}')}.")
                else:
                    print(f"Successfully uninstall {FontRed(f'{package_name}')}.")

    @abstractmethod
    def install_cmd(self):
        pass

    def set_driver_target_version(self, driver_version: str):
        self._driver_version = driver_version

    def version_lookup(self):
        if (
            self._name == CheckModuleNames.container_toolkit.name
            and self._driver_version
        ):
            return self._driver_version

        pre_component_version = None
        # TODO(@caizhi): please implement me here
        # print("=============please implement version_lookup==========")
        return pre_component_version

    def download(self):
        archive_dict = DOWNLOADER.download(self._name, self._version)
        self._pkg_path_dict.update(DownloadDecompressor(archive_dict).decompress())

    def install(self, version: str = None, path: str = None):
        self._target_version = version
        self._pkg_path_dict[self._name] = path
        # TODO(@wangkang): code needs to be optimized
        if self._name in [MusaModule.mccl.name, MusaModule.mudnn.name]:
            checker = CHECKER[CheckModuleNames.musa.name]()
        else:
            checker = CHECKER[self._name]()
        # 1. first execute check
        success_flag, status = checker.check()
        # 2. if dependency check failed, return directly
        if checker._has_dependency_failed:
            print(
                f"The pre-requisite dependency check failed. Please manually install {self._name}. For detailed check information, use the `musa-develop -c {self._name}` command!"
            )
            exit()
        # 3. if path is specified
        if path:
            self.uninstall()
            self._pkg_path_dict[self._name] = path
            self.install_cmd()
            return
        # 4. path is None, target_version is specified
        if (
            success_flag
            and (
                checker.get_version() == self._target_version
                or (self._target_version is None and checker.get_version() is None)
            )
            and self._name not in [MusaModule.mccl.name, MusaModule.mudnn.name]
        ):  # TODO(@wangkang): when install mccl or mudnn, checker is from MusaChecker
            current_version = (
                (checker.get_version() + " ") if checker.get_version() else ""
            )
            print(
                FontGreen(
                    f"{self._name} {current_version}has already been installed successfully!"
                )
            )
            return
        elif (
            success_flag
            and self._target_version is None
            and self._name not in [MusaModule.mccl.name, MusaModule.mudnn.name]
        ):  # TODO(@wangkang): when install mccl or mudnn, checker is from MusaChecker
            # 5. path is None, target_version is None and has been installed
            current_version = (
                (checker.get_version() + " ") if checker.get_version() else ""
            )
            print(
                FontGreen(
                    f"{self._name} {current_version}has already been installed successfully!"
                )
            )
            # TODO(@caizhi): need print newest version
            # if newest version != checker.get_version():
            #    print(FontGreen()
            return
        else:
            for preinstaller in self._preinstaller:
                target_pre_version = self.version_lookup()
                preinstaller._target_version = target_pre_version
                preinstaller.install(target_pre_version)
            self.uninstall()
            self.download()
            self.install_cmd()

    def update(self, version: str = None, path: str = None):
        self.uninstall()
        self.install(version, path)


class HostPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.host.name
        self._package_type = "apt"

    def download(self):
        pass

    def uninstall_cmd(self):
        """
        Used only when called by another class
        package_name: docker.io, dkms, lightdm, clinfo, ...
        """
        self._shell.run_cmd_with_error_print("apt remove dkms")
        self._shell.run_cmd_with_error_print("apt remove lightdm")

    def install_cmd(self):
        require_root_privileges_check()
        """
        package_name: docker.io, dkms, lightdm
        """
        print("Installing dkms...")
        self._shell.run_cmd_with_error_print("apt install -y dkms")
        print("Installing lightdm...")
        self._shell.run_cmd_with_error_print("apt install -y lightdm")


class DriverPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.driver.name
        self._target_package_name = "musa"
        self._package_type = "dpkg"
        self._preinstaller = [
            HostPkgMgr(),
        ]

    def uninstall_cmd(self):
        require_root_privileges_check()
        print(f"Uninstall {FontRed(f'{self._name}')} ...")
        self._shell.run_cmd_with_error_print(f"dpkg -P {self._target_package_name}")

    def install_cmd(self):
        require_root_privileges_check()
        print(f"Installing {FontGreen(f'{self._name}')} ...")
        self._shell.run_cmd_with_error_print(
            f"dpkg -i {self._pkg_path_dict[self._name]}"
        )
        # TODO(@caizhi):
        print(
            FontRed(
                "==========Please restart your machine and then continue with your task!=========="
            )
        )
        print(
            FontRed(
                "==========Please restart your machine and then continue with your task!=========="
            )
        )
        print(
            FontRed(
                "==========Please restart your machine and then continue with your task!=========="
            )
        )
        exit()


class SmartIOPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.smartio.name
        self._target_package_name = "mt-peermem"
        self._package_key = (
            "smartio"  # TODO(@wangkang): only to get package path from download
        )
        self._package_type = "dpkg"

    def load_package_cmd(self):
        pass

    def uninstall_cmd(self):
        require_root_privileges_check()
        print(f"Uninstalling {self._target_package_name}...")
        self._shell.run_cmd_with_error_print(f"dpkg -P {self._target_package_name}")

    def install_cmd(self):
        require_root_privileges_check()
        print(f"Installing {self._target_package_name}...")
        self._shell.run_cmd_with_error_print(
            f"dpkg -i {self._pkg_path_dict[self._package_key]}"
        )


class ContainerToolkitsPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.container_toolkit.name
        self._package_type = "dpkg"
        self._target_package_name = "container-toolkit"
        self._dependency_package_list = ["mtml", "sgpu-dkms"]
        self._preinstaller = [
            DriverPkgMgr(),
        ]

    def uninstall_cmd(self):
        # 1.uninstall mt-container-toolkit
        print("Uninstall mt-container-toolkit ...")
        self._shell.run_cmd_with_error_print("dpkg -P mt-container-toolkit")
        # 2.uninstall mtml
        print("Uninstall dependencies mtml ...")
        self._shell.run_cmd_with_error_print("dpkg -P mtml")
        # 3.uninstall sgpu-dkms
        print("Uninstall dependencies sgpu-dkms ...")
        self._shell.run_cmd_with_error_print("dpkg -P sgpu-dkms")

    def install_cmd(self):
        require_root_privileges_check()
        # 1.install mtml
        print("Installing mtml ...")
        self._shell.run_cmd_with_error_print(f"dpkg -i {self._pkg_path_dict['mtml']}")
        # 2.install sgpu-dkms
        print("Installing sgpu-dkms ...")
        self._shell.run_cmd_with_error_print(
            f"dpkg -i {self._pkg_path_dict['sgpu-dkms']}"
        )
        # 3.install mt-container-toolkit
        print("Installing mt-container-toolkit ...")
        self._shell.run_cmd_with_error_print(
            f"dpkg -i {self._pkg_path_dict[self._target_package_name]}"
        )
        # 4.binding
        print("Binding mthreads runtime to docker...")
        self._shell.run_cmd_with_error_print(
            "(cd /usr/bin/musa && ./docker setup $PWD)"
        )


class MusaPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.musa.name
        self._target_package_name = "musa_toolkits"
        self._package_type = "sh"
        self._is_installed_file_flag = "/usr/local/musa/lib/libmusa.so"
        if EXECUTED_ON_HOST_FLAG:
            self._preinstaller = [
                DriverPkgMgr(),
            ]

    def _add_env_to_bashrc(self) -> None:
        """
        Adds an environment variable to the user's .bashrc file and reloads it.
        """
        self._shell.run_cmd(
            f"echo 'export PATH={MUSA_BIN_PATH}:${{PATH}}' >> ~/.bashrc"
        )
        self._shell.run_cmd(
            f"echo 'export LD_LIBRARY_PATH={MUSA_LIB_PATH}:${{LD_LIBRARY_PATH}}' >> ~/.bashrc"
        )

        self._shell.run_cmd("source ~/.bashrc")

    def uninstall_cmd(self):
        print(f"Uninstall {self._target_package_name}...")
        uninstall_script_path = os.path.join(
            CURRENT_FOLDER, "uninstall_" + self._target_package_name + ".sh"
        )
        self._shell.run_cmd_with_error_print(f"bash {uninstall_script_path}")

    def install_cmd(self):
        require_root_privileges_check()
        print(f"Installing {self._target_package_name}...")
        self._shell.run_cmd_with_error_print(
            f"bash {self._pkg_path_dict[self._target_package_name]} -i"
        )

        self._add_env_to_bashrc()


class muDNNPkgMgr(PackageManager):
    def __init__(self):
        super().__init__()
        self._name = MusaModule.mudnn.name
        self._target_package_name = "mudnn"
        self._package_type = "sh"
        self._is_installed_file_flag = "/usr/local/musa/lib/libmudnn.so"
        self._preinstaller = [
            MusaPkgMgr(),
        ]

    def uninstall_cmd(self):
        print(f"Uninstall {self._target_package_name}...")
        uninstall_script_path = os.path.join(
            CURRENT_FOLDER, "uninstall_" + self._target_package_name + ".sh"
        )
        self._shell.run_cmd_with_error_print(f"bash {uninstall_script_path}")

    def install_cmd(self):
        require_root_privileges_check()
        print(f"Installing {self._target_package_name}...")
        bash_dir = os.path.dirname(self._pkg_path_dict[self._target_package_name])
        os.chdir(bash_dir)
        self._shell.run_cmd_with_error_print(
            f"bash {self._pkg_path_dict[self._target_package_name]} -i"
        )
        os.chdir(CURRENT_WORK_DIR)


class McclPkgMgr(PackageManager):
    def __init__(self):
        super().__init__()
        self._name = MusaModule.mccl.name
        self._target_package_name = "mccl"
        self._package_type = "sh"
        self._is_installed_file_flag = "/usr/local/musa/lib/libmccl.so"
        self._preinstaller = [
            MusaPkgMgr(),
        ]

    def uninstall_cmd(self):
        print(f"Uninstall {self._target_package_name}...")
        uninstall_script_path = os.path.join(
            CURRENT_FOLDER, "uninstall_" + self._target_package_name + ".sh"
        )
        self._shell.run_cmd_with_error_print(f"bash {uninstall_script_path}")

    def install_cmd(self):
        require_root_privileges_check()
        print(f"Installing {self._target_package_name}...")
        bash_dir = os.path.dirname(self._pkg_path_dict[self._target_package_name])
        os.chdir(bash_dir)
        self._shell.run_cmd_with_error_print(
            f"bash {self._pkg_path_dict[self._target_package_name]} -i"
        )
        os.chdir(CURRENT_WORK_DIR)


class TorchMusaPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = MusaModule.mudnn.name
        self._target_package_name = "torch_musa"
        self._package_type = "pip"
        self._dependency_package_list = ["torch", "torchvision", "torchaudio"]
        self._preinstaller = [
            MusaPkgMgr(),
            muDNNPkgMgr(),
            McclPkgMgr(),
        ]

    def install_cmd(self):
        print(f"Installing {self._target_package_name}...")
        self._shell.run_cmd_with_error_print(
            f"pip install {self._pkg_path_dict[self._target_package_name]}"
        )
        print(f"Installing {self._target_package_name} dependencies...")
        for package in self._dependency_package_list:
            self._shell.run_cmd_with_error_print(
                f"pip install {self._pkg_path_dict[package]}"
            )

    def uninstall_cmd(self):
        print(f"Uninstall {self._target_package_name}...")
        self._shell.run_cmd_with_error_print(
            f"pip uninstall {self._target_package_name}"
        )
        print(f"Uninstall {self._target_package_name} dependencies...")
        for package in self._dependency_package_list:
            self._shell.run_cmd_with_error_print(f"pip uninstall {package}")


class vLLMPkgMgr(PackageManager):
    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.vllm.name
        self._package_type = "pip"
        self._target_package_name = "vllm"
        self._dependency_package_list = ["mttransformer"]
        self._preinstaller = [
            TorchMusaPkgMgr(),
        ]

    def install_cmd(self):
        # 1.install dependencies
        print(f"Installing {self._target_package_name} dependencies...")
        # 1.1 install mttransformer
        self._shell.run_cmd_with_error_print(
            f"pip install {self._pkg_path_dict['mttransformer']}"
        )
        # TODO(@wangkang): requirements need test
        # 1.2 install other dependencies with requirements.txt
        vllm_requirements = os.path.join(CURRENT_FOLDER, "vllm_requirements.txt")
        self._shell.run_cmd_with_error_print(f"pip install -r {vllm_requirements}")

        # 2.install vllm
        print(f"Installing {self._target_package_name}...")
        # TODO(@wangkang): add vllm install cmd

    def uninstall_cmd(self):
        print(f"Uninstall {self._target_package_name} dependencies...")
        for package in self._dependency_package_list:
            self._shell.run_cmd_with_error_print(f"pip uninstall {package}")


class SDKPkgMgr(PackageManager):
    def __init__(self):
        super().__init__()
        self._musa_toolkit = MusaPkgMgr()
        self._mudnn = muDNNPkgMgr()
        self._mccl = McclPkgMgr()
        self._driver = DriverPkgMgr()
        self._smartio = SmartIOPkgMgr()

    # TODO(@wangkang): 暂时不考虑version匹配问题
    def install_cmd(self):
        pass

    def uninstall(self):
        self._musa_toolkit.uninstall()
        self._driver.uninstall()
        self._smartio.uninstall()
