# setup.py
from setuptools import setup

setup(
    name="hstream",
    version="0.1",
    py_modules=["main"],
    install_requires=[
        "Click",
    ],
    entry_points="""
        [console_scripts]
        hstream=__main__:hello
    """,
)
