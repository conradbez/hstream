from fastapi.staticfiles import StaticFiles

from hstream import hs

# hs.stylesheet_href = hs.list_css_frameworks()["bare.css"]

m = hs.multiselect(label=["a", "b", "c"], default_value=["a", "c"], key="multiselect")

hs.markdown(m)
