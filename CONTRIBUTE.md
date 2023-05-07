## Deploy

1. increment version in `setup.py`

2. `rm -rf build/ hstream.egg-info/ dist/`

3. `python -m build`

4. `twine upload dist/*`