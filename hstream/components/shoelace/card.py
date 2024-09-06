from hstream.components.components import ComponentsGeneric, component_wrapper

@component_wrapper
def sl_card(
    self, 
    content: str, 
    key: str = None, 
    **kwargs
) -> None:
    """
    Render a Shoelace card component.

    Args:
        content (str): The main content of the card.
        key (str, optional): A unique identifier for the card. Default is None.
        **kwargs: Additional attributes to pass to the card element.
            - header (str, optional): The content to display in the header. Default is None.
            - footer (str, optional): The content to display in the footer. Default is None.
            - image_url (str, optional): The URL of an image to display at the top of the card. Default is None.
    """
    header: str = kwargs.get("header", None)
    footer: str = kwargs.get("footer", None)
    image_url: str = kwargs.get("image_url", None)

    with self.tag("sl-card", ("id", key) if key else None):
        if header:
            with self.tag("div", ("slot", "header")):
                self.doc.text(header)
        
        if image_url:
            with self.tag("img", ("slot", "image"), ("src", image_url), ("alt", "Card image")):
                pass

        self.doc.text(content)
        
        if footer:
            with self.tag("div", ("slot", "footer")):
                self.doc.text(footer)
    
    _hs_session[key] = None  # Store session data for the card if needed
    return lambda s: s  # Card doesn't return any specific action value
