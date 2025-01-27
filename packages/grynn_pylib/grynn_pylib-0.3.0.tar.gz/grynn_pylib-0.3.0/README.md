# grynn_pylib

[![Python Tests](https://github.com/Grynn/grynn_pylib/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/Grynn/grynn_pylib/actions/workflows/pytest.yml)

This is a Python library project that provides finance-related functions and general utility functions.

## Installation

You can install the library using uv (or pip):

```shell
uv install grynn_pylib 
#OR
pip install grynn_pylib
```

## Usage

```python
from grynn_pylib import utils

pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
utils.bcompare(pd.a, pd.b)
```

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/grynn/grynn_pylib/blob/main/LICENSE) file for more information.

## Notes

* This project is a work in progress.
* py_vollib could be an alternative to the Black-Scholes formula implementation in this library.
* [optlib](https://github.com/dbrojas/optlib/tree/master) looks interesting (uses a very old numpy though, did not install on 3.12.6 out of the box)
