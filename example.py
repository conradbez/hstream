
from hstream import hs

visitor_name = hs.text_input("What's your name?", default_value = "friend")

hs.markdown(f"Welcome {visitor_name}")