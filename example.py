from hstream import hs

sliderinput1 = hs.slider('test', minValue=1, maxValue=100, default_value=5, key='sliderinput1')
hs.slider('test', minValue=1, maxValue=2, default_value=1, key='sliderinput12')

t = hs.text_input("test", '', )
hs.markdown(sliderinput1)
# hs.stylesheet_href = "https://cdn.jsdelivr.net/gh/dohliam/dropin-minimal-css/src/a11yana.css"
# # hs.stylesheet_href = hs.list_css_frameworks()["bahunya.css"]
# # with hs.html('script',
# #             ('src', "https://dohliam.github.io/dropin-minimal-css/switcher.js"),
# #             ('type', "text/javascript"),
# #              ):
# #     pass
# page = hs.nav(["Home", "Cards", "Graph"], "Home", key="nav")

# with hs.html("header"):
#     hs.markdown(
#         f"## HStream {2+2}",
#     )

# # with hs.html("section"):
# #     with hs.html("aside"):
# #         hs.markdown(
# #             f"## First aside {1}",
# #         )

# #     with hs.html("aside"):
# #         hs.markdown(
# #             f"## Second aside {1+1}",
# #         )

# #     with hs.html("aside"):
# #         hs.markdown(
# #             f"## Third aside {1+2}",
# #         )

# # hs.markdown("Make htmx website creation easy")

# # hs.markdown(f"simply write `hs.markdown(2+2)` to get {2+2}" )

# # with hs.html('form'):
# #     user_number = hs.number_input(
# #             "Input a number",
# #             default_value = 0,
# #         )

# # hs.markdown(f"test number output {user_number}")

# # hs.markdown(f"and multiply {user_number} by 2 to get {int(user_number)*2}", )

# # with hs.html('header'):
# #     with hs.html('h1'):
# #         hs.markdown("This is h1")
# #     hs.markdown("This is not a h1 but still a header")

# # with hs.html('form'):
# #     hs.markdown("Please enter your name")
# # name = hs.text_input('Name', '', key = 'test')


# # import matplotlib.pyplot as plt
# # import numpy as np
# # x = np.arange(0,4*np.pi,0.1)   # start,stop,step
# # y = np.sin(x) * float(1)
# # fig, ax = plt.subplots()
# # ax.plot(x,y)
# # hs.pyplot(fig, key='myplot')



