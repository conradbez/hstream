from hstream import hs

if hs.button(
    "Test raising an error",
):
    hs.markdown("lets run: `assert 1==2` and we should see and error message popup")
    assert 1 == 2

hs.markdown("once the error is run this code will not execute and should disappear")
