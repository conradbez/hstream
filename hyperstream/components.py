from yattag import Doc
from yattag.simpledoc import SimpleDoc
from typing import Literal, OrderedDict
from functools import wraps

from inspect import getframeinfo, stack


class Components:
    def __init__(self) -> None:
        self.return_old_doc_and_init_new()
        # self.doc, self.tag, self.text = Doc().tagtext()

    def get_key_based_on_call(self, message):
        """
        Get the concat the functions call line and arguments to get a key

        * Gothca * : f-strings are evaluated before we get to inspect them so they'll
                     cause double-ups and might need explicit keys assigned

        """
        for i in range(20):
            caller = getframeinfo(stack()[i][0])
            if str(self.path_to_user_script) in caller.filename:
                call_signiture = f"{caller.filename}, {caller.lineno}, {message}"
                key = "".join(x for x in call_signiture if x.isalpha() or x.isnumeric())
                return key

    def build_component(
        self, component_type, label=None, default_value=None, key=None, **kwargs
    ):
        """Writes a component to the SH front end

        Args:
            label (_type_, optional): Must be ubique within the app. Content to write to the web front end. Defaults to None.
            default_value (_type_, optional): default value the component returns before use enters value - will always be null for text or component where user doesn't input. Defaults to None.
        """

        # to support user's use of `with hs.tag` we first need to exit out of the context manager
        # while 'yattag.simpledoc.SimpleDoc.DocumentRoot' not in str(type(self.doc.current_tag)):

        component_key = key

        assert (
            not "_" in component_key
        ), "please don't use underscores in keys"  # we use headers to update compoennts by key but headers don't like underscores
        components = self.get_components()
        if not components.get(component_key, False):
            # if we don't have this component stored initialise it
            components[component_key] = {
                # these values shouldn't change between reruns so we set them here on initialisation
                "current_value": default_value,
                "component_key": component_key,
                "component_type": component_type,
            }

        components[component_key].update(
            {
                # these values can change between reruns (i.e. text input is outputted to a write component)
                "label": label,
            }
        )

        if kwargs:
            components[component_key].update(kwargs)
        try:
            self.write_components(
                components,
            )
        except Exception as e:
            print("error ", e)

        return components[component_key]["current_value"]

    def component_wrapper(component_fucntion):
        @wraps(component_fucntion)
        def wrapped_component_function(self, *method_args, **method_kwargs):
            if not method_kwargs.get("key", False):
                method_kwargs["key"] = self.get_key_based_on_call(method_args)
            value = self.build_component(
                **component_fucntion(self, *method_args, **method_kwargs)
            )
            return value

        return wrapped_component_function

    def return_old_doc_and_init_new(self):
        old_doc = ""
        if getattr(self, "doc", False):
            #
            # to support user's use of `with hs.tag` we first need to exit out of the context manager
            # untill we reach the root (in case we are nested deep within `with's`)
            while "yattag.simpledoc.SimpleDoc.DocumentRoot" not in str(
                type(self.doc.current_tag)
            ):
                self.doc.current_tag.__exit__(False, value=None, traceback=False)
            old_doc = str(self.doc.getvalue())

        # Refresh the doc to blank for the next element
        self.doc, self.tag, self.text = Doc().tagtext()
        return old_doc

    @component_wrapper
    def markdown(self, text: str, *, key: str = False) -> None:
        import markdown

        html = markdown.markdown(text)
        with self.tag("div"):
            self.doc.asis(html)
        display_html = self.return_old_doc_and_init_new()
        return dict(
            label=display_html,
            component_type="Markdown",
            key=key,
        )

    @component_wrapper
    def text_input(self, label: str, default_value: str, key: str = None) -> str:
        """Displays text input for user to input text

        Args:
            text (str): label to display to user describing the text input
            default_value (str): value innitially entered into text box
        Returns:
            str: text inputted by user
        """
        component_attr = self.get_components().get(key, OrderedDict())
        with self.tag("label"):
            self.text(label)
        with self.tag(
            "input",
            ("name", key),
            ("hx-post", f"/value_changed/{key}"),
            ("hx-trigger", "focusout"),
            ("type", "text"),
        ):
            pass
        html = self.return_old_doc_and_init_new()
        return dict(
            label=html, component_type="TextInput", default_value=default_value, key=key
        )

    @component_wrapper
    def number_input(self, label: str, default_value: int, key: str = None) -> str:
        """Displays text input for user to input text

        Args:
            text (str): label to display to user describing the text input
            default_value (str): value innitially entered into text box
        Returns:
            str: text inputted by user
        """
        component_attr = self.get_components().get(key, OrderedDict())
        with self.tag("label"):
            self.text(label)
        with self.tag(
            "input",
            ("name", key),
            ("hx-post", f"/value_changed/{key}"),
            ("hx-trigger", "focusout"),
            ("type", "number"),
        ):
            pass
        html = self.return_old_doc_and_init_new()
        return dict(
            label=html, component_type="TextInput", default_value=default_value, key=key
        )

    @component_wrapper
    def select_box(self, label: list[str], default_value: int, key: str = None):
        with self.doc.select(
            ("name", key),
            ("hx-post", f"/value_changed/{key}"),
            # multiple = "multiple"
        ):
            for value in label:
                with self.tag(
                    "option",
                    ("value", value),
                ):
                    self.text(value)
        html = self.return_old_doc_and_init_new()
        return dict(
            label=html, component_type="TextInput", default_value=default_value, key=key
        )

    @component_wrapper
    def slider(
        self,
        label: str,
        minValue: int,
        maxValue: int,
        default_value: int,
        key: str = None,
    ) -> str:
        """ """
        if not key:
            key = label

        kwargs = {
            "minValue": minValue,
            "maxValue": maxValue,
        }

        component_attr = self.get_components().get(key, OrderedDict())
        component_key = key
        with self.tag(
            "input",
            ("name", component_key),
            ("type", "range"),
            ("value", component_attr.get("current_value", "")),
            ("min", component_attr.get("minValue", 0)),
            ("max", component_attr.get("maxValue", 100)),
            ("hx-post", f"/value_changed/{component_key}"),
        ):
            self.text("")
        html = self.return_old_doc_and_init_new()
        return dict(
            label=html,
            component_type="Slider",
            default_value=default_value,
            key=key,
            **kwargs,
        )

    @component_wrapper
    def nav(
        self,
        label: list[str],
        default_value,
        key,
    ):
        if not key:
            key = label
        kwargs = {}
        component_attr = self.get_components().get(key, OrderedDict())
        component_value = component_attr.get('current_value', False)
        component_key = key
        with self.tag("ul"):
            for item in label:
                color = "grey" if component_value == item else ""
                with self.tag(
                    "li",
                ):
                    with self.tag(
                        "a",
                        ("href", "#"),
                        ('test', item),
                        ('style', f'color:{color}'),
                        # changing nav is currently not supported because the label isn' part of the refresh check
                        (
                            "hx-post",
                            f"/value_changed/{component_key}?{component_key}={item}",
                        ),
                    ):
                        self.text(str(item))
        html = self.return_old_doc_and_init_new()
        return dict(
            label=html,
            component_type="Nav",
            default_value=default_value,
            key=key,
            **kwargs,
        )

    @component_wrapper
    def pyplot(self, fig, key: str = None) -> None:
        """Displays matplotlib plot to user

        Args:
            fig (matplotlib.figure.Figure): label to display to user describing the text input
        Returns:
            str: text inputted by user


        Example:
            import matplotlib.pyplot as plt
            import numpy as np
            x = np.arange(0,4*np.pi,0.1)   # start,stop,step
            y = np.sin(x) * float(sine_height)
            fig, ax = plt.subplots()
            ax.plot(x,y)
            hs.pyplot(fig, key='myplot')
        """

        from base64 import b64encode
        import io

        stringIObytes = io.BytesIO()
        fig.savefig(stringIObytes, format="png")
        stringIObytes.seek(0)
        base64_data = b64encode(stringIObytes.read())
        base64_data = base64_data.decode("utf-8")

        with self.tag(
            "img",
            ("src", f"data:image/png;base64,{base64_data}"),
            ("alt", "Graph"),
        ):
            self.text("")
        html = self.return_old_doc_and_init_new()
        return dict(label=html, component_type="Image", default_value=None, key=key)
