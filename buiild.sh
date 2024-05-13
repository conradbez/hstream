rm -rf build/ hstream.egg-info/ dist/
pip install twine build
python -m build
twine upload dist/*
