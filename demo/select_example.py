from hstream import hs

user_options = ["I love HStream", "HStream could use some work", "Other"]

with hs.html("form"):
    hs.markdown("Select dropdown inside a 'form' tag")
    user_response = hs.select_box(label=user_options, default_value=user_options[0])

if user_response == user_options[0]:
    hs.markdown("Thank you for the kind words!")
elif user_response == user_options[1]:
    hs.markdown("Uft that's harsh, but thanks for the feedback!")
else:
    with hs.html("article"):
        with hs.html("aside"):
            hs.markdown("We'd love to hear from you, please send us an email!")
        with hs.html(
            "button",
            onclick="window.location.href='mailto:conradbez1@gmail.com?subject=HStream feedback'",
        ):
            hs.markdown("Send email")
