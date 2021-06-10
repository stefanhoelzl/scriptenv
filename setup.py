"""scriptenv setup script"""

from setuptools import setup

ProjectName = "scriptenv"

setup(
    name=ProjectName,
    version="0.0.1",
    url="https://github.com/stefanhoelzl/requirements/",
    author="Stefan Hoelzl",
    author_email=f"stefanh+{ProjectName}@posteo.de",
    license="MIT",
    packages=[ProjectName],
    zip_safe=False,
)
