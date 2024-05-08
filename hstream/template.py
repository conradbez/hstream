import os

dir_path = os.path.dirname(os.path.realpath(__file__))


def format_html():
    format_html = os.path.join(dir_path, "templates", "format_html.html")
    with open(format_html, "r") as file:
        format_html = file.read()
    return format_html


error_html = os.path.join(dir_path, "templates", "error_html.html")
with open(error_html, "r") as file:
    error_html = file.read()
