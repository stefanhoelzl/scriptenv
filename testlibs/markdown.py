"""pytest plugin to run python code section in markdown files."""
# pylint: disable=protected-access,exec-used
import ast
import traceback
import types
from itertools import dropwhile
from pathlib import Path
from typing import Any, Generator, Optional, Tuple, Union

import py
import pytest
from _pytest._code.code import ExceptionInfo, TerminalRepr
from _pytest.assertion.rewrite import rewrite_asserts
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from markdown_it import MarkdownIt

MarkdownFileExtensions = [".md"]


class MarkdownPythonCodeSection(pytest.Item):
    """pytest representation of a markdown python code section."""

    def __init__(self, name: str, parent: pytest.Collector, source: str, lineno: int):
        super().__init__(name, parent)
        self.source = source
        self.lineno = lineno

        self.funcargs = {}  # type: ignore
        self._fixtureinfo = None

    def setup(self) -> None:
        def func() -> None:
            pass

        self._fixtureinfo = self.session._fixturemanager.getfixtureinfo(  # type: ignore
            node=self, func=func, cls=None, funcargs=False
        )
        FixtureRequest(self, _ispytest=True)._fillfixtures()

    def runtest(self) -> None:
        tree = ast.parse(self.source)

        rewrite_asserts(
            tree, self.source.encode("utf-8"), str(self.fspath), self.config
        )

        compiled = compile(tree, str(self.fspath), "exec", dont_inherit=True)
        mod = types.ModuleType(self.name)
        exec(compiled, mod.__dict__)

    def repr_failure(
        self,
        excinfo: ExceptionInfo[BaseException],
        style: Optional[Any] = None,
    ) -> Union[str, TerminalRepr]:
        """Called when self.runtest() raises an exception."""

        frame_summaries = list(
            dropwhile(
                lambda fs: Path(fs.filename).suffix not in MarkdownFileExtensions,
                traceback.extract_tb(excinfo.tb),
            )
        )
        if frame_summaries:
            first_frame = frame_summaries[0]
            first_frame.lineno += self.lineno
            first_frame._line = (  # type: ignore
                Path(first_frame.filename)
                .read_text()
                .splitlines()[first_frame.lineno - 1]
            )
            return "".join(traceback.format_list(frame_summaries))
        return super().repr_failure(excinfo)

    def reportinfo(self) -> Tuple[Union[py.path.local, str], int, str]:
        return self.fspath, self.lineno, self.name


class MarkdownFile(pytest.File):
    """pytest markdown file representation."""

    def collect(self) -> Generator[MarkdownPythonCodeSection, None, None]:
        """Collects python code sections from a markdown file."""
        markdown = MarkdownIt()
        section = 0
        for token in markdown.parse(Path(self.fspath).read_text()):
            if token.tag == "code" and token.info == "python":
                # token.map is zero based, but first line should be shown as 1
                lineno = token.map[0] + 1 if token.map else 1
                yield MarkdownPythonCodeSection.from_parent(
                    self,
                    name=f"lineno-{lineno}",
                    source=token.content,
                    lineno=lineno,
                )
                section += 1


def pytest_collect_file(
    parent: pytest.Collector, path: py.path.local
) -> Optional[MarkdownFile]:
    """Collects all markdown files."""
    if parent.config.getoption("--markdown"):
        if path.ext in MarkdownFileExtensions:
            return MarkdownFile.from_parent(parent, fspath=path)  # type: ignore
    return None


def pytest_addoption(parser: Parser) -> None:
    """Adds a markdown option to pytest"""
    parser.addoption("--markdown", action="store_true", default=False)
