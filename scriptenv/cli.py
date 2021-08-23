"""command line interface for scriptenv"""

import argparse
import subprocess
import sys
from typing import Iterable, List, Optional

from . import requires


def run(requirements: Iterable[str], cmd: Iterable[str]) -> int:
    """Executes a package binary."""
    requires(*requirements)
    return subprocess.run(list(cmd), check=False).returncode


def main(args: Optional[List[str]] = None) -> int:
    """scriptenv cli main entrypoint"""
    if args is None:
        args = sys.argv[1:]
    elif not args:
        args = ["--help"]

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument(
        "--requires", "-r", action="store", nargs="*", type=str, default=[]
    )
    run_parser.add_argument("command", nargs="+", type=str)
    run_parser.set_defaults(func=lambda args: run(args.requires, cmd=args.command))

    parsed = parser.parse_args(args)
    return parsed.func(parsed)  # type: ignore
