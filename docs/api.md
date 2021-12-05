# API
Defining requirements
```python
import scriptenv
scriptenv.requires('rsa==4.8')

import rsa
assert rsa.__version__ == "4.8"
```

use `requires` as context manager
```python
import scriptenv

with scriptenv.requires("rsa==4.8"):
    import rsa
    assert rsa.__version__ == "4.8" 

with scriptenv.requires("rsa==4.7"):
    import rsa
    assert rsa.__version__ == "4.7" 
```