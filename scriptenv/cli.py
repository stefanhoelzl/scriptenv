"""command line interface for scriptenv"""

import argparse
import subprocess
import sys
from typing import Iterable, List, Optional

from .scriptenv import ScriptEnv


def run(requirements: Iterable[str], cmd: Iterable[str]) -> int:
    """Executes a package binary."""
    env = ScriptEnv()
    env.apply(requirements)
    return subprocess.run(list(cmd), check=False).returncode


def main(args: Optional[List[str]] = None) -> int:
    """scriptenv cli main entrypoint"""
    args = args or sys.argv[1:]

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("requirements", nargs="*")
    run_parser.add_argument("-c", "--command", action="store", nargs="+", type=str)
    run_parser.set_defaults(func=lambda args: run(args.requirements, cmd=args.command))

    parsed = parser.parse_args(args)
    return parsed.func(parsed)  # type: ignore
