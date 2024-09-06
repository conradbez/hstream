from yattag import Doc

# from hstream.components.text_input import text_input
from hstream.components.components import Components
from hstream.components.styling_components import StyledComponents
from hstream.components.shoelace_components import ShoelaceComponents

class HSDoc(Doc):
    class Tag(Doc.Tag):
        def __exit__(self, tpe, value, traceback):
            res = super().__exit__(tpe, value, traceback)
            # set_session_var("hs_html", indent(self.doc.getvalue()))
            return res


class hs(Components, StyledComponents, ShoelaceComponents):
    def __init__(self) -> (HSDoc, HSDoc.tag, HSDoc.text):
        self.doc, self.tag, self.text = HSDoc().tagtext()

    def clear(self):
        self.doc, self.tag, self.text = HSDoc().tagtext()
