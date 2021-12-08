"""scriptenv setup script"""

from pathlib import Path

from setuptools import setup
from tools.release import version

ProjectName = "scriptenv"

setup(
    name=ProjectName,
    version=version(),
    author="Stefan Hoelzl",
    author_email=f"stefanh+{ProjectName}@posteo.de",
    url="https://stefanhoelzl.github.io/scriptenv/",
    license="MIT",
    description="define virtual environments within your code",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    keywords="virtualenv virtual environment venv scripting",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development",
        "Topic :: System :: Software Distribution",
    ],
    packages=[ProjectName],
    entry_points={
        "console_scripts": ["scriptenv=scriptenv.cli:main"],
    },
    install_requires=["pip>=19.3", "appdirs"],
    zip_safe=False,
)
