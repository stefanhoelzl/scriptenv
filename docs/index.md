# Getting Started

Install `scriptenv`
```bash
$ pip install scriptenv
```

use any package you want in your REPL or short-lived scripts
```python
import scriptenv
scriptenv.requires('requests==2.25.1')

import requests
assert requests.__version__ == "2.25.1"
requests.get('http://www.google.com')
```

use a binary/entry point defined in any package
```bash
$ scriptenv run -r black==21.5b2 -- black --version
black, version 21.5b2
```