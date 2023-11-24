from hstream import hs
from pathlib import Path
import importlib

image_path = importlib.resources.files("hstream.test").joinpath(
    "h.png"
    )

image_file = open(image_path, 'rb')

# hs.image(image_file, key='test-image', width=100)


hs.nav(['Home', 'World'], logo_file=image_file)