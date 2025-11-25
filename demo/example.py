from hstream import hs

page = hs.nav(["Home", "About"], default_value="Home", key="nav")

if page == "About":
    hs.markdown("For more info visit [github](github.com/conradbez/hstream)")
else:
    with hs.html("header"):
        hs.markdown(
            """## HStream
            Offers great flexibility in developing Python web apps easily
            """,
        )

    with hs.html("section"):
        with hs.html("aside"):
            hs.markdown(
                "Simply write python scripts and instead of print use `hs.markdown` to built web outputs",
            )

        with hs.html("aside"):
            hs.markdown(
                "User inputs are as simple as `user_value = hs.text_input('Please input your text')`",
            )

        with hs.html("aside"):
            hs.markdown(
                "Run with classic web technologies means you can easily customize your app once you need to without rewriting everything",
            )

    hs.markdown(
        f"""
    #Make htmx website creation easy
    Simply write `hs.markdown(2+2)` to get {2+2}
    """
    )

    hs.markdown("""Or create forms like:""")
    with hs.html("form"):
        user_number = hs.number_input(
            "Input a number",
            default_value=0,
        )
        hs.markdown(
            f"Your number is {'*even*' if int(user_number) % 2 == 0 else '*odd*'}"
        )
    with hs.html("header"):
        hs.markdown("## HStream also supports displaying plots")
    with hs.html("section"):
        hs.markdown(
            """
        `import matplotlib.pyplot as plt`

        `import numpy as np`

        `x = np.arange(0,4*np.pi,0.1)   # start,stop,step`

        `y = np.sin(x) * float(1)`

        `fig, ax = plt.subplots()`

        `ax.plot(x,y)`

        `hs.pyplot(fig, key='myplot')`
        """
        )
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            x = np.arange(0, 4 * np.pi, 0.1)  # start,stop,step
            y = np.sin(x) * float(1)
            fig, ax = plt.subplots()
            ax.plot(x, y)
            hs.pyplot(fig, key="myplot")
        except Exception:
            hs.markdown(
                "hmmm seems you don't have matplotlib installed, please install it with `pip install matplotlib`"
            )
            # raise e
