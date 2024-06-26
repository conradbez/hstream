from hstream import hs

hs.markdown(
    """
# We're very flexible with styling, should you need it to fine tune your app post MVP

Here's an example of a slider with custom styling

- move the slider to the center of the page

- set width to 50% of the page

"""
)

hs.markdown(
    """

    with hs.doc.tag("center",):

        with hs.html('div',('style', "width: 50%;),):

            hs.slider("Pick a value", 0,100, 50)


"""
)

with hs.doc.tag(
    "center",
):
    with hs.html(
        "div",
        ("style", "width: 50%;"),
    ):
        hs.slider("Pick a value", 0, 100, 50)
