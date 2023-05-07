import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="hstream",
    version="0.0.16",
    author="Conrad Bezuidenhout",
    author_email="conradbez1@gmail.com",
    description=("Create python webapps with ease"),
    license="BSD",
    license_files = ["LICENSE"],
    keywords="streamlit htmx fastapi",
    url="https://github.com/conradbez/hstream",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
        "fastapi~=0.85",
        "uvicorn~=0.19",
        "watchfiles~=0.18",
        "Jinja2~=3.1",
        "Markdown~=3.4",
        "yattag~=1.14",
        "starlette_context==0.3.4",
        "python-multipart",
        "matplotlib",
    ],
    entry_points={"console_scripts": ["hstream = hstream.runner:run"]},
    packages=["hstream"],
    package_data={"hstream": ["templates/main.html", "templates/header.html"]},
    include_package_data=True,
)
