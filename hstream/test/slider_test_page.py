from hstream import hs

visitor_name = hs.text_input("What's your name?", default_value = "friend")

slider_value = hs.slider("Click me!", minValue=0, maxValue=100, default_value=50, key='test-slider')

if not slider_value == 50:
    hs.markdown("Element response successful", key='response-message')