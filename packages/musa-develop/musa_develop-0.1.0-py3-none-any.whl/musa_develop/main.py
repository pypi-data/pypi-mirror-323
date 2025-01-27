import os
import sys
import argparse
from .check import CHECKER
from musa_develop.install import PACKAGE_MANAGER
from .report import report
from .utils import parse_args, demo_parse_args
from .download import DOWNLOADER
from musa_develop.demo import DEMO
from musa_develop.demo.demo import DemoTask

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(
        prog="musa-develop",
        formatter_class=argparse.RawTextHelpFormatter,
        description="A tool for deploying and checking the musa environment.",
    )
    parser.add_argument(
        "-c",
        "--check",
        nargs="?",
        const="driver",
        default="",
        choices=[
            "host",
            "driver",
            "mtlink",
            "ib",
            "smartio",
            "container_toolkit",
            "torch_musa",
            "musa",
            "vllm",
            None,
        ],
        dest="check",
        help="""check musa develop environment. Default value is 'driver' if only '-c' or '--check' is set.
optional list: host
               driver
               mtlink
               ib
               smartio
               container_toolkit
               musa
               torch_musa
               vllm""",
    )
    parser.add_argument(
        "--container",
        dest="container",
        type=str,
        default=None,
        help="Check the musa environment in the container.",
    )
    parser.add_argument(
        "-r",
        "--report",
        dest="report",
        action="store_true",
        default=False,
        help="Display the software stack and hardware information of the current environment.",
    )
    parser.add_argument(
        "-d",
        "--download",
        dest="download",
        type=parse_args,
        help="""
            choices=[
                "kuae/kuae=1.3.0/kuae==1.3.0",
                "sdk/sdk=3.1.0/sdk==3.1.0",
                "musa"
                "mudnn",
                "mccl",
                "driver",
                "smartio",
                "container_toolkit",
                "torch_musa",
            ],
        """,
    )
    parser.add_argument(
        "--dir",
        nargs="?",
        type=str,
        help="""
            download dir
        """,
    )
    parser.add_argument(
        "-i",
        "--install",
        dest="install",
        type=parse_args,
        # TODO(@wangkang): 是否需要kuae参数?, 如何处理?
        help="""
            choices=[
                "kuae/kuae==1.3.0/kuae=1.3.0/kuae--1.3.0/kuae-1.3.0",
                "sdk/sdk==3.1.0/sdk=3.1.0/sdk--3.1.0/sdk-3.1.0",
                "mudnn",
                "mccl",
                "driver",
                "musa/musa_toolkits"
                "smartio",
                "container_toolkit",
                "torch_musa",
            ],
        """,
    )
    parser.add_argument(
        "-p",
        "--path",
        nargs="?",
        type=str,
        help="""
            install file path
        """,
    )
    parser.add_argument(
        "-u",
        "--uninstall",
        dest="uninstall",
        help="""
            choices=[
                "musa",
                "sdk",
                "mudnn",
                "mccl",
                "driver",
                "smartio",
                "container_toolkit",
                "torch_musa",
                "vllm",
            ],
        """,
    )
    parser.add_argument(
        "--update",
        dest="update",
        type=parse_args,
        # TODO(@wangkang): 是否需要kuae参数?, 如何处理?
        help="""
            choices=[
                "kuae/kuae==1.3.0/kuae=1.3.0/kuae--1.3.0/kuae-1.3.0",
                "sdk/sdk==3.1.0/sdk=3.1.0/sdk--3.1.0/sdk-3.1.0",
                "mudnn",
                "mccl",
                "driver",
                "musa/musa_toolkits"
                "smartio",
                "container_toolkit",
                "torch_musa",
            ],
        """,
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="Print verbose",
    )

    # =====================demo=====================
    demo_parser = parser.add_argument_group("Demo Mode")
    demo_parser.add_argument(
        "--demo",
        dest="demo",
        type=demo_parse_args,
        help="""Run the built-in AI demo, specifying the product name, product version, and whether to run it inside a Docker container.
            choices=[
                "torch_musa",
                "torch_musa==1.3.0/torch_musa--1.3.0",
                "torch_musa=1.3.0/torch_musa-1.3.0",
                "torch_musa==docker/torch_musa--docker",
                "torch_musa=docker/torch_musa-docker",
                "torch_musa==1.3.0==docker/torch_musa=1.3.0=docker",
                "torch_musa--1.3.0--docker/torch_musa-1.3.0-docker",
                "vllm",
                "vllm==0.4.0/vllm--0.4.0",
                "vllm=0.4.0/vllm-0.4.0",
                "vllm==docker/vllm=docker",
                "vllm--docker/vllm-docker",
                "vllm==0.4.0==docker/vllm=0.4.0=docker",
                "vllm--0.4.0--docker/vllm-0.4.0-docker",
            ],
        """,
    )
    # Task Options
    task_options = DemoTask()
    demo_parser.add_argument(
        "-t",
        "--task",
        dest="task",
        type=str,
        default="base",
        choices=task_options.get_all_task(),
        help=f"""Run a specified task (must be used with --demo).
choices:
{task_options.get_all_task()}""",
    )

    demo_parser.add_argument(
        "--ctnr-name",
        dest="ctnr_name",
        type=str,
        default=False,
        help="Optionally, specify a container name (must be used with --demo).",
    )

    demo_parser.add_argument(
        "--host-dir",
        dest="host_dir",
        type=str,
        default=False,
        help="Optionally, specify a host directory mapping to the container (must be used with --demo).",
    )

    demo_parser.add_argument(
        "--ctnr-dir",
        dest="ctnr_dir",
        type=str,
        default=False,
        help="Optionally, specify a container directory mapping from host (must be used with --demo).",
    )

    # ===========================================

    # default with no args will print help
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    # ====================check===================
    if args.container and not args.check:
        parser.error("--container can only be used with -c/--check")
        return

    if args.check:
        checker = CHECKER[args.check](container_name=args.container)
        checker.check()
        checker.report()
        return

    # ====================report===================
    if args.report:
        report()
        return

    # ====================download===================
    if args.download:
        download_name, download_version = args.download
        DOWNLOADER.download(download_name, download_version, args.dir)
        return

    # ====================install===================
    if args.install:
        install_name, install_version = args.install
        PACKAGE_MANAGER[install_name].install(install_version, args.path)
        return

    # =====================uninstall=====================
    if args.uninstall:
        PACKAGE_MANAGER[args.uninstall].uninstall()
        return

    # ====================update===================
    if args.update:
        install_name, install_version = args.update
        PACKAGE_MANAGER[install_name].update(install_version, args.path)
        return

    # =====================demo=====================
    if not args.demo:
        if args.task or args.ctnr_name or args.host_dir or args.ctnr_dir:
            parser.error(
                "The --demo option is required when using --task, --host-dir, or --ctnr-name."
            )
            exit()
    else:
        if args.ctnr_dir:
            if not args.host_dir:
                parser.error("'--host-dir' must be specified when using '--ctnr-dir'")

        if args.ctnr_name:
            print(f"Container name: {args.ctnr_name}")

        if args.host_dir:
            if not args.ctnr_dir:
                args.ctnr_dir = "/workspace"
                print(f"Directory on host: {args.host_dir}.")
                print("The Directory will mapping to the container: /workspace .")
            else:
                print(f"Directory on host: {args.host_dir}.")
                print(f"The Directory will mapping to the container: {args.ctnr_dir}.")
        # task args check
        if not args.task:
            args.task = "base"
            print("Without specifying a task, start a container runs on MT-GPU. ")
        if args.task not in task_options.get_all_task():
            parser.error(
                f"task '{args.task}' is invalid, choose from {task_options.get_all_task()}"
            )
        demo, version, use_docker = args.demo
        DEMO[demo].start(version, args.task, use_docker)
    # ============================================


if __name__ == "__main__":
    main()
