# Getting Started

Install `scriptenv`
```bash
$ pip install scriptenv
```

use any package you want in your REPL or short-lived scripts
```python
import scriptenv
scriptenv.requires('rsa==4.8')

import rsa
assert rsa.__version__ == "4.8"
rsa.newkeys(32)
```

use a binary/entry point defined in any package
```bash
$ scriptenv run -r black==21.5b2 -- black --version
black, version 21.5b2
```