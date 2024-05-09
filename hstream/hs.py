from yattag import Doc, indent
import yattag

# from hstream.components.text_input import text_input
from hstream.components.components import Components
from hstream.components.styling_components import StyledComponents
from hstream.utils import set_session_var


class HSDoc(Doc):
    class Tag(Doc.Tag):
        def __exit__(self, tpe, value, traceback):
            res = super().__exit__(tpe, value, traceback)
            set_session_var("hs_html", indent(self.doc.getvalue()))
            return res


class hs(Components, StyledComponents):
    def __init__(self) -> (yattag.SimpleDoc, yattag.Doc.tag, yattag.Doc.text):
        self.doc, self.tag, self.text = HSDoc().tagtext()

    def clear(self):
        self.doc, self.tag, self.text = HSDoc().tagtext()
