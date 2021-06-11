"""scriptenv setup script"""

from setuptools import setup
from scriptenv import __version__, __author__

ProjectName = "scriptenv"

setup(
    name=ProjectName,
    version=__version__,
    url="https://github.com/stefanhoelzl/requirements/",
    author=__author__,
    author_email=f"stefanh+{ProjectName}@posteo.de",
    license="MIT",
    packages=[ProjectName],
    install_requires=["pip>=19.3", "appdirs"],
    zip_safe=False,
)
