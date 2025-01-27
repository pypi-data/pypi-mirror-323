# Sample Python Package

This is a sample package built for learning python packaging.

To build and publish package, install following:

```
python3 -m pip install build twine
```

## Build Package

using setuptools

```
python3 -m build
```

check the packages if it complies to PyPI

```
twine check dist/*
```

## Publish

once built, publish to PyPi.

get the API token from PyPI.

- open account [page](https://pypi.org/manage/account)
- go to `API tokens`
- click on `Add API token`
- configure
- copy the generated token

use twine to upload the distribution packages. Configure twine to use PyPI token, edit `$HOME/.pypirc`

```
[pypi]
username = __token__
password = ${API_TOKEN}
repository = https://upload.pypi.org/legacy/
```

upload the package:

```
python3 -m twine upload --repository pypi dist/*
```