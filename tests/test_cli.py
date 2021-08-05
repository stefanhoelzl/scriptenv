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
def env(mocker: MockerFixture) -> Mock:
    return mocker.patch("scriptenv.cli.ScriptEnv")


def test_run_executes_subprocess(subprocess_run: Mock) -> None:
    cli.run([], cmd=["cmd", "arg"])
    subprocess_run.assert_called_once_with(["cmd", "arg"], check=False)


def test_run_returns_returncode(subprocess_run: Mock) -> None:
    subprocess_run.return_value.returncode = 1
    assert cli.run([], cmd=[]) == 1


def test_run_env_created_before_starting_subprocess(
    subprocess_run: Mock, env: Mock
) -> None:
    parent_mock = Mock()
    parent_mock.attach_mock(subprocess_run, "subprocess")
    parent_mock.attach_mock(env, "env")

    cli.run(["requirement"], [])

    parent_mock.assert_has_calls(
        [
            call.env(),
            call.env().apply(["requirement"]),
            call.subprocess([], check=False),
        ]
    )


def test_main_forward_return_value(mocker: MockerFixture) -> None:
    mocker.patch.object(cli, "run").return_value = 1
    assert cli.main(["run", "-c", "cmd"]) == 1


def test_main_run_parser(mocker: MockerFixture) -> None:
    run_mock = mocker.patch.object(cli, "run")

    cli.main(["run", "-c", "cmd"])
    run_mock.assert_called_with([], cmd=["cmd"])

    cli.main(["run", "--command", "cmd"])
    run_mock.assert_called_with([], cmd=["cmd"])

    cli.main(["run", "--command", "cmd", '"with spaces"'])
    run_mock.assert_called_with([], cmd=["cmd", '"with spaces"'])

    cli.main(["run", "requirement0", "requirement1", "-c", "cmd", "arg"])
    run_mock.assert_called_with(["requirement0", "requirement1"], cmd=["cmd", "arg"])
