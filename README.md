# scriptenv
State requirements inside your python script and `scriptenv` will make them available.

# Getting Started
Install `scriptenv` and you can use any package you want in your short-lived scripts.
```bash
$ pip install scriptenv
$ python -c "import scriptenv; scriptenv.pin('requests==2.25.1'); import requests; requests.get('http://www.google.com')"
```

# Why Another Venv/Package Manager Project
The goal of this project is to provide a way to define your dependencies in your script you want to run
and requires no extra setup steps for a virtual env.

The scope is for small scripts you want to share or you only want to run from time to time.
For sharing scripts it is also not necessary anymore to also share a `requirements.txt` file.

# How It Works
`scriptenv` installs every dependency it ever sees in a seperate folder 
and prepends the folders for the defined dependencies in a script to `sys.path`.
