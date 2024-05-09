from hstream import hs
from time import sleep

# with hs.tag('style'):

hs.set_primary_color(
    attribute_to_style="primary-background",
    color="blue",
    color_intensity=400,
)

hs.set_primary_color(
    attribute_to_style="primary-hover-background", color="blue", color_intensity=100
)

with hs.tag("button"):
    hs.text("Test")
# hs.markdown(t)
hs.markdown("test")
if hs.button(
    "Test raising an error",
):
    hs.markdown("lets run: `assert 1==2` and we should see and error message popup")
    assert 1 == 2

if hs.button("Test raising an error", full_width=True):
    hs.markdown("lets run: `assert 1==2` and we should see and error message popup")
    assert 1 == 2
