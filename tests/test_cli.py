# pylint: disable=missing-module-docstring,missing-function-docstring,redefined-outer-name,unused-argument

from subprocess import CompletedProcess
from unittest.mock import Mock, call

import pytest
from pytest_mock import MockerFixture

from scriptenv import cli


@pytest.fixture(autouse=True)
def subprocess_run(mocker: MockerFixture) -> Mock:
    mock = mocker.patch("subprocess.run")
    mock.return_value = CompletedProcess(args=[], returncode=0)
    return mock


@pytest.fixture(autouse=True)
def requires(mocker: MockerFixture) -> Mock:
    return mocker.patch("scriptenv.cli.requires")


def test_run_executes_subprocess(subprocess_run: Mock) -> None:
    cli.run([], cmd=["cmd", "arg"])
    subprocess_run.assert_called_once_with(["cmd", "arg"], check=False)


def test_run_returns_returncode(subprocess_run: Mock) -> None:
    subprocess_run.return_value.returncode = 1
    assert cli.run([], cmd=[]) == 1


def test_run_env_created_before_starting_subprocess(
    subprocess_run: Mock, requires: Mock
) -> None:
    parent_mock = Mock()
    parent_mock.attach_mock(requires, "requires")
    parent_mock.attach_mock(subprocess_run, "subprocess")

    cli.run(["requirement0", "requirement1"], [])

    parent_mock.assert_has_calls(
        [
            call.requires("requirement0", "requirement1"),
            call.subprocess([], check=False),
        ]
    )


def test_run_from_main(mocker: MockerFixture) -> None:
    mocker.patch.object(cli, "run").return_value = 1
    assert cli.main(["run", "cmd"]) == 1


def test_main_run_parser(mocker: MockerFixture) -> None:
    run_mock = mocker.patch.object(cli, "run")

    cli.main(["run", "cmd"])
    run_mock.assert_called_with([], cmd=["cmd"])

    cli.main(["run", "cmd", '"with spaces"'])
    run_mock.assert_called_with([], cmd=["cmd", '"with spaces"'])

    cli.main(["run", "-r", "requirement0", "--", "cmd", "arg"])
    run_mock.assert_called_with(["requirement0"], cmd=["cmd", "arg"])

    cli.main(["run", "--requires", "requirement0", "--", "cmd", "arg"])
    run_mock.assert_called_with(["requirement0"], cmd=["cmd", "arg"])

    cli.main(["run", "-r", "requirement0", "requirement1", "--", "cmd", "arg"])
    run_mock.assert_called_with(["requirement0", "requirement1"], cmd=["cmd", "arg"])


def test_main_without_args() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main([])
    assert exc_info.value.code == 0
