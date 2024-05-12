import importlib
import glob
import os

from hstream import hs

files = glob.glob("./demo/*.py")
for f in files:
    if os.path.basename(f) == "example.py":
        continue

file = hs.nav([os.path.basename(f) for f in files[:4]], default_value="example.py")


importlib.import_module(f'demo.{file.split(".")[0]}')

# exec(open(f'./demo/{file}').read())
