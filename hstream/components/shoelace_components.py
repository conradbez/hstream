from hstream.components.components import ComponentsGeneric, component_wrapper
from typing import List
class ShoelaceComponents(ComponentsGeneric):
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
