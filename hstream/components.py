from yattag import Doc
from yattag.simpledoc import SimpleDoc
from typing import List, Literal, OrderedDict
from functools import wraps
from pathlib import Path
from inspect import getframeinfo, stack


class Components:
    def get_key_based_on_call(self, message):
        """
        Get the concat the functions call line and arguments to get a key

        * Gothca * : loop will be on the same line and therefor get the same key,
                     we need the user to specify a key in that case
                     this case is not checked for atm

        """
        for i in range(20):
            caller = getframeinfo(stack()[i][0])
            if str(self.path_to_user_script) in caller.filename:
                # breakpoint()
                call_signiture = f"{Path(caller.filename).stem}, {caller.lineno}"
                key = "".join(x for x in call_signiture if x.isalpha() or x.isnumeric())
                return key

    def component_value(self, default_value=None, key=None, **kwargs):
        """Writes a component to the SH front end

        Args:
            label (_type_, optional): Must be ubique within the app. Content to write to the web front end. Defaults to None.
            default_value (_type_, optional): default value the component returns before use enters value - will always be null for text or component where user doesn't input. Defaults to None.
        """

        # to support user's use of `with hs.tag` we first need to exit out of the context manager
        # while 'yattag.simpledoc.SimpleDoc.DocumentRoot' not in str(type(self.doc.current_tag)):

        assert (
            not "_" in key
        ), f"please don't use underscores in keys, found in {key}"  # we use headers to update compoennts by key but headers don't like underscores
        components = self.get_components()
        return components.get(key, default_value)

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
                ("id", method_kwargs["key"]),
                # ("hx-get",f"/content/{key}"),
                ("hx-trigger", f"none"),
                # ('hx-swap', "morph"),
            ):
                component_fucntion(self, *method_args, **method_kwargs)
            # if there is no current value let subsitute the default value

            return value

        return wrapped_component_function

    @component_wrapper
    def markdown(self, text: str, key: str = False, **kwargs) -> None:
        import markdown

        html = markdown.markdown(str(text))
        with self.tag(
            "div",
        ):
            self.doc.asis(html)

    @component_wrapper
    def text_input(
        self, label: str, default_value: str = "", key: str = None, **kwargs
    ) -> str:
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
            ("hx-swap", "none"),
            ("type", "text"),
            ("value", str(kwargs["value"])),
        ):
            pass

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
            ("name", key),
            ("hx-post", f"/value_changed/{key}"),
            ("hx-trigger", "focusout"),
            ("type", "number"),
            ("value", str(kwargs["value"])),
        ):
            pass

    @component_wrapper
    def select_box(
        self, label: List[str], default_value: str = False, key: str = None, **kwargs
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
            ("name", key),
            ("hx-post", f"/value_changed/{key}"),
        ):
            for value in label:
                with self.tag(
                    "option",
                    ("value", value),
                ):
                    if kwargs["value"] == value:
                        self.doc.attr(selected='')

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
        
        assert type(label)==type([]) and type(default_value)==type([]), "multiselect requires a list of options and a list of default values"

        # HStream developer note: The default value logic is handled by the `@component_wrapper`
        js_to_get_all_select_values = f"""
        Array.from(document.querySelectorAll('#{key} option:checked')).map(el => el.value).toString()
            """
        if type(kwargs["value"]) == type(""):
            # the frontend returns the value as a string of comma seperated values
            currently_selected_values = kwargs["value"].split(',')
        elif type(kwargs["value"]) == type([]):
            currently_selected_values = kwargs["value"]
        else:
            raise "multi select current value seems corrupted"

        with self.doc.select(
            ("name", key),
            ('id', key),
            ("hx-post", f"/value_changed/{key}"),
            ("multiple", ""),
            # transform the multiselect value into a list of selected indexes like "1,2,7"
            ("hx-vals", "js:{"+key+" : "+js_to_get_all_select_values+"}"),
            ("hx-trigger", "focusout")
        ):
            for value in label:
                assert not "," in value, "multiselect options can't contain commas"
                with self.tag(
                    "option",
                    ("value", value),
                    ("selected", "") if value in currently_selected_values else ''
                ):
                    self.text(value)

    # @component_wrapper
    # def dropdown(
    #     self, label: List[str], default_value: List[int] = [], key: str = None, **kwargs
    # ) -> List[int]:
    #     js_to_get_all_select_values = f"""
    #     extractCheckedCheckboxValues("#{key}.map(el => el.value).toString()
    #         """
    #     js_to_get_all_select_values = f"""console.log('hi')"""
        
    #     with self.tag('script', 
    #                   ('type', 'text/javascript'),
    #                   ):
    #         self.doc.asis("""
    #         function extractCheckedCheckboxValues(elementId) {
    #             const element = document.getElementById(elementId);
                
    #             if (!element) {
    #                 console.error(`Element with ID '${elementId}' not found.`);
    #                 return [];
    #             }
                
    #             const checkboxes = element.querySelectorAll('input[type="checkbox"]:checked');
    #             const values = Array.from(checkboxes).map((checkbox) => checkbox.value);
                
    #             return values;
    #             }
    #         """)

    #     if type(kwargs['value']) == type([]):
    #         value = kwargs['value']
    #     elif type(kwargs['value']) == type(""):
    #         value = kwargs['value'].split(',')
    #     else:
    #         value =  kwargs['value']

    #     with self.tag('details', 
    #             ('role','list'),
    #             ('key', key),
    #             ('id', key),
    #             # ('onfocus', f'(e) => console.log(extractCheckedCheckboxValues("{key}"))'),
    #             # ("hx-trigger", f"click from:#{key}-submit"),
    #             ("hx-post", f"/value_changed/{key}"),
    #             ("hx-vals", "js:{"+key+" : "+f'extractCheckedCheckboxValues("{key}")'+"}"),
    #             ("hx-trigger", f"revealed from:#{key}-dropdown-option"),
    #             ):
    #         with self.tag('summary', ('aria-haspopup','listbox')):
    #             self.text('Dropdown')
    #         with self.tag('ul', 
                        
    #                     ('role','listbox'),
    #                     ):
    #             with self.tag('li'):
    #                 for option in label:
    #                     with self.tag('label'):
    #                         self.doc.input(
    #                             ('id', f'{key}-dropdown-option'),
    #                             ('name', 'option') ,
    #                             ('type','checkbox'),
    #                             ('value', option),
    #                             ('checked' if option in value else '', ''),
    #                         )
    #                         self.text(option)
    #     with self.tag("button",
    #                   ('onclick', f'console.log(extractCheckedCheckboxValues("{key}"))'),
    #                   ('id',f"{key}-submit"),
    #                   ):
    #         self.text('done')

    @component_wrapper
    def slider(
        self,
        label: str,
        minValue: int,
        maxValue: int,
        default_value: int,
        key: str = None,
        **kwargs,
    ) -> str:
        """ """
        with self.tag("label", ("for", key)):
            self.text(label)
        with self.tag(
            "input",
            ("name", key),
            ("id", key),
            ("type", "range"),
            ("value", str(kwargs["value"])),
            ("min", minValue),
            ("max", maxValue),
            ("hx-post", f"/value_changed/{key}"),
        ):
            pass

    @component_wrapper
    def nav(
        self,
        label: List[str],
        default_value,
        key,
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
                        color = "grey" if kwargs["value"] == item else ""
                        with self.tag(
                            "li",
                            ("hx-trigger", "click"),
                            (
                                "hx-post",
                                f"/value_changed/{key}?{key}={item}",
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
        with self.tag("label", ("for", key)):
            self.text(label)
        with self.tag(
            "input",
            ("id", key),
            ("type", "checkbox"),
            (
                "checked"
                if kwargs["value"] in ["true", True, 1, "1"]
                else "notchecked",
                "",
            ),
            # annoyingly a blank checkbox is not sent back in a submit event,
            # so we attach the state of the checkbox here
            # https://htmx.org/attributes/hx-vals/, https://github.com/bigskysoftware/htmx/issues/894
            ("hx-vals", "js:{" + key + ": event.srcElement.checked}"),
            ("hx-post", f"/value_changed/{key}"),
        ):
            pass

    @component_wrapper
    def button(
        self,
        label: str,
        default_value: bool = False,
        key: str = None,
        **kwargs,
    ) -> str:
        """ """
        with self.tag(
            "button",
            ("id", key),
            ("type", "submit"),
            ("hx-vals", '{nav:"true"}'),
            ("hx-post", f"/value_changed/{key}?{key}=true"),
            ("hx-swap", "none"),
        ):
            self.text(label)
