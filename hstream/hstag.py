from yattag import Doc
from yattag.simpledoc import _attributes
import shelve
from typing import OrderedDict

HS_HTML_CONSTANT = "html"  # constant used in the key of component to indicate it is raw html producted by this component


class HsDoc(Doc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tag(self, tag_name, *args, **kwargs):
        return self.__class__.Tag(
            self,
            tag_name,
            _attributes(args, kwargs),
            path_to_app_db=kwargs.get("path_to_app_db", "app_db"),
        )

    class Tag(Doc.Tag):
        def __init__(self, *args, **kwargs):
            path_to_app_db = kwargs.pop("path_to_app_db")
            super().__init__(*args, **kwargs)
            self.path_to_app_db = path_to_app_db

        def set_app_db(self, path):
            self.path_to_app_db = path

        def __enter__(self):
            super().__enter__()
            with shelve.open(str(self.path_to_app_db)) as app_db:
                components = app_db.get("components", OrderedDict())
                # print(self.doc.current_tag.name)
                # raise self.doc.current_tag.name
                components[
                    f"{HS_HTML_CONSTANT}{len(components)}"
                ] = f"<{self.doc.current_tag.name}>"
                app_db["components"] = components

        def __exit__(self, tpe, value, traceback) -> None:

            with shelve.open(str(self.path_to_app_db)) as app_db:
                components = app_db.get("components", OrderedDict())
                components[
                    f"{HS_HTML_CONSTANT}{len(components)}"
                ] = f"</{self.doc.current_tag.name}>"
                app_db["components"] = components
            super().__exit__(tpe, value, traceback)
