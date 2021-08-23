# API
Defining requirements
```python
import scriptenv
scriptenv.requires("requests==2.25.1")

import requests
assert requests.__version__ == "2.25.1"
```

use `requires` as context manager
```python
import scriptenv

with scriptenv.requires("requests==2.25.1"):
    import requests
    assert requests.__version__ == "2.25.1" 

with scriptenv.requires("requests==2.25.0"):
    import requests
    assert requests.__version__ == "2.25.0" 
```