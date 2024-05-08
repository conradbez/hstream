from hstream import hs
from time import sleep

hs.nav(["test"])

t = hs.text_input(
    "test",
)

b = hs.button("test", "test123")
if b:
    hs.markdown(b)
