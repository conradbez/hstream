from hstream import hs

hs.markdown('test')

sl_ms = hs.sl_multiselect(['test1', 'test2', 'test3'], default_value=['test2'])
sl_ms = hs.sl_button('Shoelace button')

hs.markdown(sl_ms)

hs.button('Normal button')