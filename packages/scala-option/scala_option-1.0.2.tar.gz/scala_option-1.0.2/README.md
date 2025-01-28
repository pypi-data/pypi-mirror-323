# scala-option

<!-- Badges: -->
[![python](https://img.shields.io/badge/Python->=_3.12-3776AB.svg?style=flat&logo=python&logoColor=yellow)](https://www.python.org)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/scala-option)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/scala-option)
![Test Coverage](https://img.shields.io/badge/test_coverage-88%25-green)
![License](https://img.shields.io/badge/License-MIT-blue)

Scala like `Option` type in Python.

Implements the child classes `None` and `Some`, but renamed to `none` and
`some`, since `None` is a built-in type in Python.

## Table of Contents

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Installing Using PIP](#installing-using-pip)
  - [Building from Source](#building-from-source)
- [Usage](#quick-start)
  - [Quick Start](#quick-start)
  - [Implemented Methods](#implemented-methods)
- [License](#license)

## Installation

### Requirements

This library requires Python 3.12 or newer, because it uses the latest syntax
for generics, introduced in Python 3.12.

[Download Python](https://www.python.org/downloads/)

You can check your python version by running the command:

> Windows:
> ```pwsh
> py --version
> ```
>
> Linux and macOS:
> ```bash
> python3 --version
> ```

You can download Python from: [Download Python](https://www.python.org/downloads/)

### Installing Using PIP

You can install the package by running the command:

```bash
pip install scala-option
```

### Building from Source

First, clone the repository or download source code from the latest release.

Next, install the `build` package:

```bash
pip install build
```

Then, build the project by running:

> Windows:
> ```pwsh
> py -m build
> ```
>
> Linux and macOS:
> ```bash
> python -m build
> ```


To install the package locally, run:

```bash
pip install -e .
```

## Usage

### Quick Start

Once you have installed the package (see [Installation](#installation)), you
just need to add the import statement:

__Attention:__ the package name contains an underscore instead of a dash

```py
from scala_option import Option, none, some
```

Then you can begin using the `Option` type. Here's a little example:

```py
import random
from scala_option import Option, none, some

def fivety_fivety() -> Option[int]:
  if random.random() <= 0.5:
    return some(1)
  else:
    return none

def print_option(option: Option) -> None:
  if option.is_empty():
    print("You got nothing!")
  else:
    print(f"You got something: {option.get()}")
```

### Implemented Methods

The `Option` type implements many of the most important methods
of the Scala `Option` ([Scala Option documentation](https://dotty.epfl.ch/api/scala/Option.html)).

The methods are documented using Docstrings.

List of methods:

- `get()`
- `is_empty()`
- `non_empty()`
- `get_or_else(default)`
- `or_else(alternative)`
- `map(f)`
- `flat_map(f)`
- `fold(if_empty, f)`
- `filter(p)`
- `exists(p)`
- `contains(elem)`
- `to_list()`

## License

[MIT License](LICENSE)
