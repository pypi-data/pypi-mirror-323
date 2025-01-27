# scala_option

<!-- Badges: -->
[![python](https://img.shields.io/badge/Python->=_3.12-3776AB.svg?style=flat&logo=python&logoColor=yellow)](https://www.python.org)
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

This library requires Python 3.12.0 or newer, because it uses the latest syntax
for generics, introduced in Python 3.12.

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

### Installing Using PIP

You can install the package by running the command:

```bash
pip install scala_option
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
> python3 -m build
> ```


To install the package locally, run:

```bash
pip install -e .
```

## Usage

### Quick Start

Once you have installed the package (see [Installation](#installation)), you
just need to add the import statement:

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

Implements some of the most important methods of the Scala `Option`
([documentation](https://dotty.epfl.ch/api/scala/Option.html)).

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
