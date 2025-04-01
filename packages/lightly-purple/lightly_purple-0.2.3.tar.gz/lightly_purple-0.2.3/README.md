# Project Purple (Python library)

## Structure

Structure of the project is inspired by [Kenneth Reitz](https://docs.python-guide.org/writing/structure/)

```bash
README.md
LICENSE
setup.py
requirements.txt
sample/__init__.py
sample/core.py
sample/helpers.py
docs/conf.py
docs/index.rst
tests/test_basic.py
tests/test_advanced.py
```

We would like to keed modular structure and separate the concerns.

### Quickstart

1. Prepare your dataset in YOLO format and ensure you have a `dataset.yaml` file. For a quick start, you can use the example dataset provided in `lightly_purple/lightly_purple/example.py`.

2. Launch the application:

```bash
make start
```

This command will:

-   Build both the backend and frontend components
-   Start the application
-   Automatically open your default browser to http://localhost:8001 (tested on MacOS)

After starting, you'll have access to:

Web application:
http://localhost:8001/

Documentation about exposed routes:
http://localhost:8001/docs

API endpoints:
http://localhost:8001/api

## Development

If you are using VS Code I would highly recommend to install the following extensions:

[vscode-black](https://github.com/34j/vscode-black)

[ruff-vscode](https://github.com/astral-sh/)

## Build

```bash
make build
```

## Usage example

You can find in the [example.py](./lightly_purple/example.py) file an example of how to use the library.

```python

from lightly_purple.dataset.loader import DatasetLoader

DatasetLoader.launch("some directory from script")

```
