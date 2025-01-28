# CodeCapture

CodeCapture is a context manager that enables capturing blocks of code while running it. This is
meant for educational purposes, e.g., extracting blocks of code from a file for inclusion in
readers. 

```python
>>> from code_capture import CodeCapture
>>> with CodeCapture("foo"):
        foo = 3
        bar = "test "
        foobar = foo * bar
        print(foobar)
test test test
>>> print(CodeCapture.store.foo)
foo = 3
bar = "test "
foobar = foo * bar
print(foobar)
```

## Installation

```bash
pip install code-capture
```

## Context manager

CodeCapture captures all code within the associated code block, based on the indentation of the
code block. 

## Bunch

The capture code blocks are stored in the `CodeCapture.store` bunch. This allows for dot-access to
the stored values. However, you can also treat `CodeCapture.store` as a dictionary, e.g.,
`CodeCapture.store['foo']` equals `CodeCapture.store.foo`. 

For more information, see https://pypi.org/project/bunch-py3/.

## Acknowledgement

The code for this project was largely copied from [Grayden's](https://stackoverflow.com/users/10441476/g-shand)
answer to [this stackoverflow question](https://stackoverflow.com/a/78485159/2658502). 
