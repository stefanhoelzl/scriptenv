# scriptenv
[![Build Status](https://github.com/stefanhoelzl/scriptenv/workflows/push/badge.svg)](https://github.com/stefanhoelzl/scriptenv/actions)
[![PyPI](https://img.shields.io/pypi/v/scriptenv.svg)](https://pypi.org/project/scriptenv/)
[![License](https://img.shields.io/pypi/l/scriptenv.svg)](LICENSE)

State requirements inside your python code and `scriptenv` makes ready to import.

## Getting Started
Install `scriptenv`
```bash
$ pip install scriptenv
```

and you can use any package you want in your REPL or short-lived scripts
```python
import scriptenv
scriptenv.requires('requests==2.25.1')

import requests
assert requests.__version__ == "2.25.1"
requests.get('http://www.google.com')
```

## Why Another Venv/Package Manager Project
The goal of this project is to provide a way to define your dependencies in your script you want to run
and requires no extra setup steps for a virtual env.

The scope is for small scripts you want to share or you only want to run from time to time.
For sharing scripts it is also not necessary anymore to also share a `requirements.txt` file.
It works also within your REPL.

## How It Works
`scriptenv` installs every dependency it ever sees in a seperate folder 
and prepends the folders for the defined dependencies in a script to `sys.path`.

## Development
### Getting Started
Open in [gitpod.io](https://gitpod.io#github.com/stefanhoelzl/scriptenv)

Get the code
```bash
$ git clone https://github.com/stefanhoelzl/scriptenv.git
$ cd scriptenv
```

Optionally you can create a [venv](https://docs.python.org/3.8/library/venv.html)
```bash
$ python -m venv venv
$ source venv/bin/activate
```

Install required python packages
```bash
$ pip install -r dev-requirements.txt -e .
```

Run tests and file checks
```bash
$ pytest
```

Trigger a new release build
```bash
$ python release.py release-candidate
```