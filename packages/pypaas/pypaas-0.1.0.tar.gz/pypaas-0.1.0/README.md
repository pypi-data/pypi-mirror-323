# pypaas
Python as a Service (pypaas)

A library for creating Python-based tasks without worrying about deployment.


## Installation
```bash
pip install pypaas
```

## Usage
```python
from pypaas import task

@task
def my_task():
    print('This runs in the cloud whenever I want :)')
```