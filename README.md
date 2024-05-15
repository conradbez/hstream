# HStream

Convert your script to interactive python web app like so:

    user_said = hs.text_input("What would you like to say:")

Powered by [Django](https://github.com/django/django) + [htmx](https://github.com/bigskysoftware/htmx) enables easy app ejection to scale/extend once you've outgrown HStream. Inspired by [Streamlit](https://github.com/streamlit/streamlit).

## Usage

`pip install hstream`

`hstream init # populates example.py`

`hstream run example.py`

![hstream demo](./demo/example.png)

## Motivation

Write beautiful user interfaces that enable quick iteration for Proof-of-Concept (PoC) python scripts, without the need to start over when we go to production.

Love Streamlit but:

- impossible to customise beyond PoC phase
- hard to reason about when extending and deploying
- non-standard approach doesn't play nicely with existing ecosystems

H-(html)-Stream is built with semantic html, Django and htmx to provide a fast and simple framework for rapid web app development that follows traditional frontend/server architecture (or at least follow it closer than Streamlit).

## Some features that excite us

- [Eject to a Django (traditional web app)](docs/features/eject.md)
- Display pandas dataframes, plots, markdown and more! [see supported components](docs/features/components.md)

[Some examples]((./demo))

## Technologies

Big thanks to the following libraries in particular


- Streamlit
- htmx
- Yattag
- pico css
- Django

## Backlog (WIP)

- [x] live server reload on file change (through univorn)
- [x] semantic html and basic html manipulation from within script
- [x] basic components - see below
- [x] swap stylesheet
- [x] complex html manipulation from within script (setting attributes)
- [x] plotly plot support
- [x] select component
- [x] multi select component
- [ ] auto ssl certs for easy deployment
- [ ] example component architecture
- [ ] reload browser on code change
