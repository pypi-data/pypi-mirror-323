# Instructions

## Setup
More details here: https://packaging.python.org/en/latest/tutorials/packaging-projects/

### Starting the virtual environment

If you don't have one already setup, you'll need to create new one and then source it.
```bash
python3 -m venv .venv && source .venv/bin/activate
```

### Installing the dependencies

```bash
pip install -r requirements.txt
```

## Publishing to TestPyPI

Install necessary build tools if not present

```bash
pip3 install build twine
```

Bump your version in `pyproject.toml`, and build your package first (delete dist folder if it exists)

```bash
python3 -m build
```

Then publish to TestPyPI

```bash
python3 -m twine upload --repository testpypi dist/*
```

Then you can consume the test package with this command:

```bash
pip3 install --index-url https://test.pypi.org/simple/ kimtrace
```

If it already exists, then you'll need to `pip3 uninstall kimtrace` first, then follow up with the command above. If there are new dependencies,
you will most likely need to run `pip3 install kimtrace` to install them.
