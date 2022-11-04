from hyperstream import hs

text_entered = hs.text_input(text = 'text_input_label', default_value='default_value', key = 'myinput')
hs.write('test')
hs.write(text_entered, key='1')

import plotly.express as px
fig =px.scatter(x=range(10), y=range(10))

hs.plotly_output(fig, key='testplot')