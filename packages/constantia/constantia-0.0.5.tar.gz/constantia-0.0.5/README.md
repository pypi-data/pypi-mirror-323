# constantia

![test](https://github.com/diegojromerolopez/constantia/actions/workflows/test.yml/badge.svg)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/diegojromerolopez/constantia/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/constantia.svg)](https://pypi.python.org/pypi/constantia/)
[![PyPI version constantia](https://badge.fury.io/py/constantia.svg)](https://pypi.python.org/pypi/constantia/)
[![PyPI status](https://img.shields.io/pypi/status/constantia.svg)](https://pypi.python.org/pypi/constantia/)
[![PyPI download month](https://img.shields.io/pypi/dm/constantia.svg)](https://pypi.python.org/pypi/constantia/)
[![Maintainability](https://api.codeclimate.com/v1/badges/2866bb9c56abf9223384/maintainability)](https://codeclimate.com/github/diegojromerolopez/constantia/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/2866bb9c56abf9223384/test_coverage)](https://codeclimate.com/github/diegojromerolopez/constantia/test_coverage)

Enforce constants in your code at import or at run time.

## Usage
Use the `consts` decorator and pass as parameters a list of
variables you want to treat as constants.

The variables in the constant list cannot be re-assigned nor they
can be assigned a mutable object. They can only be assigned:
- strings
- integers
- floats
- tuples

This is done to avoid indirect modifications.

Choose if you want to do the checks at runtime or when importing
the function by setting the check_at argument.

## Examples

### Function

#### Checking the constants at import time

```python
from constantia import consts

@consts(['x', 'y', 'z'], check_at='import')
def func():
    x = [1, 2, 3] # this will crash at import time as the constant does not have an immutable value
    y = 20
    y = 30  # this will raise an exception at import time as the constant is reassigned
```

#### Checking the constants at run time

```python
from constantia import consts

@consts(['x', 'y', 'z'], check_at='runtime')
def func():
    x = [1, 2, 3] # this will rais an exception when trying to run the function
    y = 20
    y = 30  # this will rais an exception when trying to run the function
```

### Class constants

#### Ensuring every uppercase attribute is a constant

```python
from constantia import consts

@consts('uppercase', check_at='import')
class Example:
    X = 9999
    Y = 'other constant'
    X = 888  # this will raise an exception
```

#### Ensuring a constant is not re-assignable

```python
from constantia import consts

@consts(['X'], check_at='import')
class Example:
    X = 9999
    X = 888  # this will raise an exception

    @classmethod
    def change_x1(cls):
        cls.X = 8888  # this will raise an exception

    @staticmethod
    def change_x2():
        Example.X = 8888  # this will raise an exception
```

#### Sensible defaults: constants are uppercase and check the constants at import time

```python
from constantia import consts

@consts
class Example:
    X = 9999
    Y = 'other constant'
    X = 888  # this will raise an exception
```

## Dependencies
This package has no dependencies.

## License
[MIT](LICENSE) license, but if you need any other contact me.
