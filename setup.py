"""scriptenv setup script"""

import ast
from pathlib import Path

from setuptools import setup


def _get_value(name: str) -> str:
    return next(  # type: ignore
        # on python<=3.7 we have to deal with ast.Str and not ast.Constant
        getattr(node.value, "value", node.value.s)  # type: ignore
        for node in ast.parse(Path("scriptenv/__init__.py").read_text()).body
        if isinstance(node, ast.Assign)
        if node.targets[0].id == name  # type: ignore
    )


ProjectName = "scriptenv"

setup(
    name=ProjectName,
    version=_get_value("__version__"),
    url="https://github.com/stefanhoelzl/scriptenv/",
    author=_get_value("__author__"),
    author_email=f"stefanh+{ProjectName}@posteo.de",
    license="MIT",
    packages=[ProjectName],
    install_requires=["pip>=19.3", "appdirs"],
    zip_safe=False,
)
