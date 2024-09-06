from hstream.components.components import ComponentsGeneric, component_wrapper
from typing import List, Optional, Any
from hstream.components.shoelace.card import sl_card
from hstream.components.shoelace.format_date import sl_format_date

class ShoelaceComponents(ComponentsGeneric):
    
    sl_card = sl_card
    sl_format_date = sl_format_date

    @component_wrapper
    def sl_button(
        self, label: str, default_value: List[str] = None, key: str = None, **kwargs
    ) -> None:
        """
        Render a Shoelace button component.

        Args:
            label (str): The text to display on the button.
            variant (str, optional): The button's visual variant. Default is "default".
            size (str, optional): The button's size. Default is "medium".
            key (str, optional): A unique identifier for the button. Default is None.
            **kwargs: Additional attributes to pass to the button element.
        """
        variant: str = kwargs.get("variant", "default") 
        size: str = kwargs.get("size", "medium")
        with self.tag(
            "sl-button",
            ("variant", variant),
            ("size", size),
            ("hx-get", f"/set_component_value?component_id={key}&new_value=true"),
            ("hx-trigger", "click"),
        ):
            self.doc.text(label)
        _hs_session[  # noqa: F821
            key
        ] = False  # set the button back to false after it has been clicked
        return lambda s: True if s in ["True", "true", True] else False

    @component_wrapper
    def sl_input(
        self, label: str, default_value: Any = None, key: Optional[str] = None, **kwargs
    ) -> None:
        """
        Render a Shoelace input component.

        Args:
            label (str): The label for the input field.
            default_value (Any, optional): The default value for the input. Default is None.
            key (str, optional): A unique identifier for the input. Default is None.
            **kwargs: Additional attributes to pass to the input element.
                Possible attributes include:
                - type: The type of input (e.g., "text", "number", "email", etc.)
                - placeholder: Placeholder text for the input
                - size: The size of the input field
                - disabled: Whether the input is disabled
                - readonly: Whether the input is read-only
        """
        input_type = kwargs.get("type", "text")
        placeholder = kwargs.get("placeholder", "")
        size = kwargs.get("size", "medium")
        disabled = "disabled" if kwargs.get("disabled", False) else ""
        readonly = "readonly" if kwargs.get("readonly", False) else "false"
        with self.tag(
            "sl-input",
            ("name", "new_value"),
            ("type", input_type),
            ("label", label),
            ("placeholder", placeholder),
            ("size", size),
            (disabled, ""),
            (readonly, ""),
            ("value", str(kwargs['value']) if kwargs['value'] is not None else ""),
            ("hx-get", f"/set_component_value?component_id={key}"),
            ("hx-trigger", "sl-change"),
        ):
            pass
        return lambda x: x[0] if type(x) == list else x

    @component_wrapper
    def sl_multiselect(
        self, label: List[str], default_value: List[str] = None, key: str = None, **kwargs
    ) -> None:
        options = [ f'<sl-option value="{option}">{option}</sl-option>' for option in label]
        assert default_value is None or all([d in label for d in default_value]), f"Default value must be in options: {default_value} not in {label} - default_value must also be itterable"
        value = ' '.join(list(kwargs["value"] )) if default_value else ''

        with self.tag(
                "sl-select",
                ("value", value),
                ("name", "new_value"),
                ("multiple", "" ),
                ("clearable", ""),
                ("hx-post", f"/set_component_value?component_id={key}"),
                ("hx-trigger", "sl-hide"),
            ):
                self.doc.asis(''.join(options))
