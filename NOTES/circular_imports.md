### file1.py 

```python
from file2 import foo


def bar():
    return "something"
```


### file2.py

```python

def foo():
    return "hello world"


from file1 import bar

```