
## Todo
- move the `argsparse` in `hyperstream.py` to a click function
- make `hstag` acceot attributes similiat to yattag


## Deploy

1. increment version in `setup.py`

2. `rm -rf build/ hstream.egg-info/ dist/`

3. `python -m build`

4. `twine upload dist/*`