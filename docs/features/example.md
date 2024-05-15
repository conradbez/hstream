
## Ease of use

See by the [example](./demo/example.py) above how intuitive building with HStream is?

```
# example.py

from hstream import hs
page = hs.nav(["Home", "About"],default_value="Home", key="nav")

if page == "About":
    hs.markdown("For more info visit [github](github.com/conradbez/hstream)")

with hs.html("header"):
    hs.markdown(
        """## HStream
        Offers great flexibility in developing Python web apps easily
""",
    )

```

And as you can see we get a fully interactive web app - ready for deployment!

![hstream demo](./demo/example_demo.gif)
