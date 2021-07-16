"""scriptenv setup script"""

from pathlib import Path

from setuptools import setup

from release import version

MetadataTemplate = '''"""auto generated by setup.py"""

Version = "{version}"
Author = "{author}"
'''

ProjectName = "scriptenv"
Author = "stefanhoelzl"
Version = version()


Path(ProjectName, "metadata.py").write_text(
    MetadataTemplate.format(author=Author, version=Version)
)

setup(
    name=ProjectName,
    version=Version,
    description="define virtual environments within your code",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
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
    keywords="virtualenv virtual environment venv scripting",
    url="https://github.com/stefanhoelzl/scriptenv/",
    author=Author,
    author_email=f"stefanh+{ProjectName}@posteo.de",
    license="MIT",
    packages=[ProjectName],
    install_requires=["pip>=19.3", "appdirs"],
    zip_safe=False,
)
