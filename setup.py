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
    url="https://github.com/stefanhoelzl/scriptenv/",
    author=Author,
    author_email=f"stefanh+{ProjectName}@posteo.de",
    license="MIT",
    packages=[ProjectName],
    install_requires=["pip>=19.3", "appdirs"],
    zip_safe=False,
)
