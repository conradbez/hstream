## Deploy

1. increment version in `setup.py`

2. `rm -rf build/ hstream.egg-info/ dist/`

3. `pip install twine build`

4. `python -m build`

5. `twine upload dist/*`