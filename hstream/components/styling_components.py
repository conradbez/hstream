from string import Template
from typing import Literal, Tuple
from hstream.components.components import ComponentsGeneric, component_wrapper


Color = Literal[
    "red",
    "pink",
    "fuchsia",
    "purple",
    "violet",
    "indigo",
    "blue",
    "azure",
    "cyan",
    "jade",
    "green",
    "lime",
    "yellow",
    "amber",
    "pumpkin",
    "orange",
    "sand",
    "grey",
    "zinc",
    "slate",
]

ColorIntensity = Literal[
    50,
    100,
    150,
    200,
    250,
    300,
    350,
    400,
    450,
    500,
    550,
    600,
    650,
    700,
    750,
    800,
    850,
    900,
    950,
]


CssProperties = Literal[
    "background-color",
    "color",
    "text-selection-color",
    "muted-color",
    "muted-border-color",
    "primary",
    "primary-background",
    "primary-border",
    "primary-underline",
    "primary-hover",
    "primary-hover-background",
    "primary-hover-border",
    "primary-hover-underline",
    "primary-focus",
    "primary-inverse",
    "secondary",
    "secondary-background",
    "secondary-border",
    "secondary-underline",
    "secondary-hover",
    "secondary-hover-background",
    "secondary-hover-border",
    "secondary-hover-underline",
    "secondary-focus",
    "secondary-inverse",
    "contrast",
    "contrast-background",
    "contrast-border",
    "contrast-underline",
    "contrast-hover",
    "contrast-hover-background",
    "contrast-hover-border",
    "contrast-hover-underline",
    "contrast-focus",
    "contrast-inverse",
    "box-shadow",
    "h1-color",
    "h2-color",
    "h3-color",
    "h4-color",
    "h5-color",
    "h6-color",
    "mark-background-color",
    "mark-color",
    "ins-color",
    "del-color",
    "blockquote-border-color",
    "blockquote-footer-color",
    "button-box-shadow",
    "button-hover-box-shadow",
    "table-border-color",
    "table-row-stripped-background-color",
    "code-background-color",
    "code-color",
    "code-kbd-background-color",
    "code-kbd-color",
    "form-element-background-color",
    "form-element-selected-background-color",
    "form-element-border-color",
    "form-element-color",
    "form-element-placeholder-color",
    "form-element-active-background-color",
    "form-element-active-border-color",
    "form-element-focus-color",
    "form-element-disabled-opacity",
    "form-element-invalid-border-color",
    "form-element-invalid-active-border-color",
    "form-element-invalid-focus-color",
    "form-element-valid-border-color",
    "form-element-valid-active-border-color",
    "form-element-valid-focus-color",
    "switch-background-color",
    "switch-checked-background-color",
    "switch-color",
    "switch-thumb-box-shadow",
    "range-border-color",
    "range-active-border-color",
    "range-thumb-border-color",
    "range-thumb-color",
    "range-thumb-active-color",
    "accordion-border-color",
    "accordion-active-summary-color",
    "accordion-close-summary-color",
    "accordion-open-summary-color",
    "card-background-color",
    "card-border-color",
    "card-box-shadow",
    "card-sectioning-background-color",
    "dropdown-background-color",
    "dropdown-border-color",
    "dropdown-box-shadow",
    "dropdown-color",
    "dropdown-hover-background-color",
    "loading-spinner-opacity",
    "modal-overlay-background-color",
    "progress-background-color",
    "progress-color",
    "tooltip-background-color",
    "tooltip-color",
]


class StyledComponents(ComponentsGeneric):

    @component_wrapper
    def set_primary_color(
        self,
        # label: Tuple[Literal["blue", 'orange'], Literal[100, 200, 300, 400, 500, 600, 700, 800, 900]],
        default_value: bool = False,
        key: str = None,
        attribute_to_style: CssProperties = "primary-background",
        color: Color = "orange",
        color_intensity: ColorIntensity = 500,
        for_theme: Literal["light", "dark"] = "light",
        **kwargs,
    ):
        """
        Sets the primary color for the web app

        Example: `set_primary_color('blue', 500)` or `set_primary_color('orange', 500)
        """
        color_string = f"--pico-color-{color}-{str(color_intensity)}"

        style = """
        [data-theme=${for_theme}],
            :root:not([data-theme=dark]) {
            --pico-${attribute_to_style}: var(${chosen_color});
            }
            """
        style = Template(style).substitute(
            chosen_color=color_string,
            attribute_to_style=attribute_to_style,
            for_theme=for_theme,
        )
        with self.tag("style"):
            self.text(style)
        self.text("Test")
