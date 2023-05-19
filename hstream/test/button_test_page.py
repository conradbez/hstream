from hstream import hs

visitor_name = hs.text_input("What's your name?", default_value = "friend")

button_pressed = hs.button("Click me!", key='test-button')

if button_pressed:
    hs.markdown("Element response successful", key='response-message')