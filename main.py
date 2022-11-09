from hyperstream import hs

with hs.html("header"):
    hs.markdown(
        f"## HyperStream {2+2}",
    )

# hs.markdown("Make htmx website creation easy")

# hs.markdown(f"simply write `hs.markdown(2+2)` to get {2+2}" )
# with hs.html('form'):
user_number = hs.number_input(
    "Input a number",
    0,
)

hs.markdown(f"test number output {user_number}")

# hs.markdown(f"and multiply {user_number} by 2 to get {user_number*2}", )

# nav = hs.nav(list(range(10)), 4, key='nav1')

# with hs.html('header'):
#     with hs.html('h1'):
#         hs.markdown("This is h1")
#     hs.markdown("This is not a h1 but still a header")

# with hs.html('form'):
#     hs.markdown("Please enter your name")
#     name = hs.text_input('Name', '', key = 'test')

# with hs.html('table'):

#     hs.markdown(f"Hi, {name}", key = 'hi')

# t = hs.text_input('test', 'test', key='textinput12')

# import matplotlib.pyplot as plt
# import numpy as np
# x = np.arange(0,4*np.pi,0.1)   # start,stop,step
# y = np.sin(x) * float(1)
# fig, ax = plt.subplots()
# ax.plot(x,y)
# hs.pyplot(fig, key='myplot')


# hs.slider('test', minValue=1, maxValue=100, default_value=5, key='textinput1')
# hs.slider('test', minValue=1, maxValue=2, default_value=1, key='textinput124312')
