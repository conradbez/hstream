from typing import List, Literal, Tuple
from functools import wraps
from pathlib import Path
from inspect import getframeinfo, stack
import cherrypy


def component_wrapper(component_fucntion):
    @wraps(component_fucntion)
    def wrapped_component_function(self, *method_args, **method_kwargs):
        # if we arn't provided a key let make one
        key = method_kwargs.get("key", False)
        if not key:
            key = self.get_key_based_on_call(method_args)
            method_kwargs["key"] = key
        value = self.component_value(
            default_value=method_kwargs.get("default_value", None),
            key=method_kwargs["key"],
        )
        method_kwargs["value"] = value
        with self.tag(
            "div",
            ("id", f"container_for_{method_kwargs['key']}"),
            ("hx-trigger", f"none"),
        ):
            # each component should return a function that formats the user value stored in the session
            # after sent back by htmx
            user_input_formatting_fn = component_fucntion(
                self, *method_args, **method_kwargs
            )
        # if there is no current value let subsitute the default value

        if user_input_formatting_fn != None:
            return user_input_formatting_fn(value)
        else:
            # temporary while we get all components to return a function
            return value

    return wrapped_component_function


class ComponentsGeneric:
    def get_key_based_on_call(self, message):
        """
        Get the concat the functions call line and arguments to get a key

        * Gothca * : loop will be on the same line and therefor get the same key,
                     we need the user to specify a key in that case
                     this case is not checked for atm
        """
        for i in range(20):
            # import ipdb; ipdb.set_trace()
            inspect_caller = getframeinfo(stack()[i][0])
            if "HS_STREAM_USER_FILE" in inspect_caller.filename:
                call_signiture = (
                    f"{Path(inspect_caller.filename).stem}, {inspect_caller.lineno}"
                )
                key = "".join(x for x in call_signiture if x.isalpha() or x.isnumeric())
                return key

    def component_value(self, default_value=None, key=None, **kwargs):
        """Writes a component to the SH front end

        Args:
            label (_type_, optional): Must be unique within the app. Content to write to the web front end. Defaults to None.
            default_value (_type_, optional): default value the component returns before use enters value - will always be null for text or component where user doesn't input. Defaults to None.
        """
        return cherrypy.session.get(key, default_value)


class Components(ComponentsGeneric):
    @component_wrapper
    def markdown(self, text: str, key: str = False, **kwargs) -> None:
        import markdown

        # import ipdb; ipdb.set_trace()
        html = markdown.markdown(str(text))
        with self.tag(
            "div",
        ):
            self.doc.asis(html)

    @component_wrapper
    def text_input(
        self,
        label: str,
        default_value: str = "",
        key: str = None,
        placeholder: str = False,
        **kwargs,
    ) -> str:
        """Displays text input for user to input text

        Args:
            text (str): label to display to user describing the text input
            default_value (str): value innitially entered into text box
        Returns:
            str: text inputted by user
        """
        with self.tag("label"):
            self.text(label)
        with self.tag(
            "input",
            ("hx-ext", "debug"),
            ("name", "new_value"),
            ("hx-post", f"/set_component_value?component_id={key}"),
            ("hx-swap", "none"),
            ("type", "text"),
        ):
            if kwargs["value"]:
                self.doc.attr(value=str(kwargs["value"]))
            elif placeholder:
                self.doc.attr(placeholder=placeholder)
        return lambda x: str(x)

    def html(self, *args, **kwargs):
        return self.tag(*args, **kwargs)

    @component_wrapper
    def number_input(
        self, label: str, default_value: int = 0, key: str = None, **kwargs
    ) -> str:
        """Displays text input for user to input text
        Args:
            text (str): label to display to user describing the text input
            default_value (str): value innitially entered into text box
        Returns:
            str: text inputted by user
        """
        with self.tag("label"):
            self.text(label)
        with self.tag(
            "input",
            ("name", "new_value"),
            ("hx-post", f"/set_component_value?component_id={key}"),
            ("hx-trigger", "focusout"),
            ("type", "number"),
            ("value", str(kwargs["value"])),
        ):
            pass

    @component_wrapper
    def select_box(
        self, label: List[str], default_value: str = None, key: str = None, **kwargs
    ) -> str:
        """
        Dropdown component for user to select from a list of options

        Args:
            label (List[str]): Options to display to user
            default_value (str, optional): Value to select when component load the first time. Defaults to False.
            key (str, optional): Unique key - default is set based on label (options) so set this if there are multiple inputs with same label argument. Defaults to None.

        Returns:
            str: Selected value
        """
        # HStream developer note: The default value logic is handled by the `@component_wrapper`
        with self.doc.select(
            ("name", "new_value"),
            ("hx-post", f"/set_component_value?component_id={key}"),
        ):
            for value in label:
                with self.tag(
                    "option",
                    ("value", value),
                ):
                    if kwargs["value"] == value:
                        self.doc.attr(selected="")

                    self.text(str(value))

    @component_wrapper
    def multiselect(
        self, label: List[str], default_value: List[int] = [], key: str = None, **kwargs
    ) -> List[int]:
        """
        Dropdown component for user to select multiple options from a list and returns a comma separated string of the  of selected options

        Args:
            label (List[str]): Options to display to user
            default_value (str, optional): Value to select when component load the first time. Defaults to False.
            key (str, optional): Unique key - default is set based on label (options) so set this if there are multiple inputs with same label argument. Defaults to None.

        Returns:
            str: Selected value
        """

        assert type(label) == type([]) and type(default_value) == type(
            []
        ), "multiselect requires a list of options and a list of default values"

        # HStream developer note: The default value logic is handled by the `@component_wrapper`
        if type(kwargs["value"]) == type(""):
            # the frontend returns the value as a string of comma seperated values
            currently_selected_values = kwargs["value"].split(",")
        elif type(kwargs["value"]) == type([]):
            currently_selected_values = kwargs["value"]
        else:
            raise "multi select current value seems corrupted"

        with self.doc.select(
            ("name", "new_value"),
            ("id", key),
            ("hx-post", f"/set_component_value?component_id={key}"),
            ("multiple", ""),
            # transform the multiselect value into a list of selected indexes like "1,2,7"
            # ("hx-vals", "js:{"+key+" : "+js_to_get_all_select_values+"}"),
            ("hx-trigger", "focusout"),
        ):
            for value in label:
                assert not "," in value, "multiselect options can't contain commas"
                with self.tag(
                    "option",
                    ("value", value),
                    ("selected", "") if value in currently_selected_values else "",
                ):
                    self.text(value)

        return lambda x: [x] if type(x) == type("") else x

    @component_wrapper
    def multi_dropdown(
        self, label: List[str], default_value: List[int] = [], key: str = None, **kwargs
    ) -> List[int]:
        with self.tag(
            "form",
            ("id", key),
            ("hx-post", f"/set_component_value?component_id={key}"),
            # ("hx-trigger", "click from:input[type=checkbox]"),
        ):
            with self.tag(
                "details",
                ("class", "dropdown"),
                ("name", "new_value"),
                ("multiple", ""),
            ):
                with self.tag("summary", ("style", "overflow:hidden;")):
                    for v in kwargs["value"]:
                        with self.tag("kbd"):
                            self.text(v)
                with self.tag("ul"):
                    with self.tag("li"):
                        for option in label:
                            with self.tag("label"):
                                checked = (
                                    ("checked", "")
                                    if option in kwargs["value"]
                                    else ("not_checked", "")
                                )
                                self.doc.input(
                                    ("name", option),
                                    ("type", "checkbox"),
                                    ("value", option),
                                    checked,
                                )
                                self.text(option)
                    with self.tag("button", ("type", "submit")):
                        self.text("submit")
        return lambda x: list(x.keys()) if type(x) == type({}) else x

    @component_wrapper
    def slider(
        self,
        label: str,
        minValue: int,
        maxValue: int,
        default_value: int = None,
        key: str = None,
        **kwargs,
    ) -> str:
        """ """
        with self.tag("label", ("for", key)):
            self.text(label)
        with self.tag(
            "input",
            ("name", "new_value"),
            ("id", key),
            ("type", "range"),
            ("value", str(kwargs["value"])),
            ("min", minValue),
            ("max", maxValue),
            ("hx-post", f"/set_component_value?component_id={key}"),
        ):
            pass

    @component_wrapper
    def nav(
        self,
        label: List[str],
        key,
        default_value=None,
        **kwargs,
    ):
        hyperscript = f"""
        on load log #hs-nav then 
        if #nav-content in #hs-nav exists
            remove #nav-content in #hs-nav
        end then
        remove @_ from #nav-content
        put me into #hs-nav then
        set @style to display:block
                """

        with self.tag(
            "header",
            ("id", "nav-content"),
            ("_", hyperscript),
            (
                "style",
                "display:none",
            ),  # so when this is first inserted the visitors screen doesn't jump
            ("visibility", "hidden"),
        ):
            with self.tag(
                "nav",
            ):
                with self.tag("ul"):
                    for item in label:
                        if type(item) == type(lambda x: x):
                            # handle functions
                            item()

                        elif type(item) == type(""):
                            # handle string navs
                            color = "grey" if kwargs["value"] == item else ""
                            with self.tag(
                                "li",
                                ("hx-trigger", "click"),
                                (
                                    "hx-post",
                                    f"/set_component_value/?component_id={key}&new_value={item}",
                                ),
                                ("hx-swap", "none"),
                            ):
                                with self.tag(
                                    "a",
                                    # ("style", f"color:{color}"),
                                ):
                                    self.text(str(item))

    @component_wrapper
    def pyplot(self, fig, height="200px", key: str = None, **kwargs) -> None:
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
            (
                "height",
                height,
            ),  # we set the height manually so swapping images doesn't cause a page jump (due to size 100 -> 0 -> 100)
        ):
            pass

    @component_wrapper
    def checkbox(
        self,
        label: str,
        default_value: bool = False,
        key: str = None,
        **kwargs,
    ) -> str:
        """ """
        bool_checker_fromat_fn = (
            lambda user_checkbox_value: user_checkbox_value == "True"
        )
        value = bool_checker_fromat_fn(kwargs["value"])
        with self.tag("label", ("for", key)):
            with self.tag(
                "input",
                ("id", key),
                ("type", "checkbox"),
                (
                    "checked" if value else "notchecked",
                    "",
                ),
                # annoyingly a blank checkbox is not sent back in a submit event,
                # so we attach the state of the checkbox here
                # https://htmx.org/attributes/hx-vals/, https://github.com/bigskysoftware/htmx/issues/894
                # ("hx-vals", "js:{" + key + ": event.srcElement.checked}"),
                # ("hx-post", f"/set_component_value?component_id={key}"),
                (
                    "hx-post",
                    f"/set_component_value/?component_id={key}&new_value={not value}",
                ),
            ):
                pass
            self.text(label)
        return bool_checker_fromat_fn

    @component_wrapper
    def button(
        self,
        label: str,
        default_value: bool = False,
        key: str = None,
        full_width: bool = False,
        **kwargs,
    ) -> bool:
        """ """
        with self.tag(
            "button",
            ("id", key),
            ("type", "submit") if full_width else ("type", "button"),
            ("hx-trigger", "click"),
            ("hx-post", f"/set_component_value/?component_id={key}&new_value=true"),
            ("hx-swap", "none"),
        ):
            self.text(label)
        cherrypy.session[key] = False
        return lambda s: True if s in ["True", "true", True] else False

    def grid(self, *args, **kwargs):
        return self.tag("div", ("class", "grid"), *args, **kwargs)

    def write_dataframe(self, df, key, striped=False, **kwargs) -> None:
        """Writes a dataframe to the

        Args:
            df (pd.DataFrame): Dataframe to write to the web front end
            key (str): Must be unique within the app. Used to reference the dataframe in the front end
        """
        with self.tag(
            "div",
            klass="overflow-auto",
        ):
            html = (
                df.to_html(classes="", border="", justify="unset")
                .replace('style="text-align: unset;"', "")
                .replace('class="dataframe"', f'class="{striped}"')
            )
            self.doc.asis(html)
