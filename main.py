from hyperstream import hs

sine_height = hs.text_input(text = 'Sine height', default_value='3', key = 'myinput')
hs.write(f"Sine height of {sine_height}", key='1')

import matplotlib.pyplot as plt
import numpy as np
x = np.arange(0,4*np.pi,0.1)   # start,stop,step
y = np.sin(x) * float(sine_height)
fig, ax = plt.subplots()
ax.plot(x,y)
hs.pyplot(fig, key='myplot')

