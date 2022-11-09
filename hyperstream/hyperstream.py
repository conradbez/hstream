from random import randint
from pathlib import Path
import sys
import builtins
import shelve
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates
from typing import OrderedDict
import os
from yattag import Doc
from .components import Components
from .hstag import HsDoc, HS_HTML_CONSTANT
from .hstag import HsDoc


# Flow of StreamHTML
# - User script run and each call to sh.write is recorded in a shelve db
# - fast api routes are built of values in shelve
# - initial html is built off shelve (maps to fast api routes)
# - home route added to fast api
#
#  Considerations
# On code changes (fast api handles reload)

templates = Jinja2Templates(directory="templates")
emit = {"server_should_reload": False}


class Hyperstream(Components):
    def __init__(self):

        self.app = FastAPI(debug=True, middleware=middleware)
        self.path_to_user_script = Path(os.getcwd()) / Path(sys.argv[1])
        self.path_to_usesr_directory = Path(os.getcwd())
        self.path_to_app_db = Path(os.getcwd()) / "app_db"
        #
        # this is sctrictly for building html from within compoennts),
        # a tweaked version of Yattag is used for html creation from within user's scripts
        # see `hstag.py`
        self.doc, self.tag, self.text = Doc().tagtext()

        self._queue_user_script_rerun = True
        # on init we start fresh
        self.clear_components()
        self.clear_component_refresh_queue(all_component=True)

    def __call__(self):
        """Builds all our paths and returns app so the server (uvicorn) can run the built app

        Returns:
            FastAPI()
        """
        self.build_fastapi_app()

        @self.app.get("/update")
        async def should_components_update(request: Request, response: Response):
            components = self.get_component_refresh_queue()
            # see if we need to do a full refresh (usually if content is generated inside a conditional value based on hs)
            if "_full_page" in components:
                response.headers["HX-Refresh"] = "true"
                self.clear_component_refresh_queue(all_component=True)
                return str(response.headers["HX-Refresh"])
            else:
                # htmx expect multiple triggers in JSON format - see: https://github.com/bigskysoftware/htmx/issues/1030
                # final form should be {"mycomponentkeyEven":"", "mysecondcomponentkeyEven":""}
                import json

                response.headers["HX-Trigger"] = json.dumps({c: "" for c in components})
                # gotcha here is that fastapi transforms any "_" to a "-" in the header values
                return str(response.headers["HX-Trigger"])

        # Add some code to check if the python scrippt should run before we respond
        @self.app.middleware("http")
        async def evaluate_user_code_middleware(
            request: Request,
            call_next,
        ):
            response = Response("Internal server error", status_code=500)
            hs_user_id = request.cookies.get("hs_user_id", False)
            if not hs_user_id:
                hs_user_id = str(randint(100000, 1000000))
                context.hs_user_app_db_path = self.path_to_usesr_directory / str(
                    hs_user_id
                )
                print("hs_user_id2", hs_user_id)
            else:
                context.hs_user_app_db_path = self.path_to_usesr_directory / str(
                    hs_user_id
                )
                print(context.hs_user_app_db_path)
            print("hs_user_id", hs_user_id)
            if request.url.path == "/":
                # assert context.hs_user_app_db_path
                # if this is the first request we clean all state
                self.clear_components()
                self.clear_component_refresh_queue(all_component=True)
                self.run_user_script()

            elif self._queue_user_script_rerun:
                self.run_user_script()

            assert context.hs_user_app_db_path
            response = await call_next(request)

            response.set_cookie("hs_user_id", hs_user_id)
            return response

        return self.app

    def html(self, *args, **kwargs):
        doc, tag, text = HsDoc().tagtext()
        kwargs["path_to_app_db"] = path_to_app_db = self.get_app_db_path()
        return tag(*args, **kwargs)

    def get_app_db_path(self):
        """
        Get the app path regardless if we're getting from the user's code or from fastapi

        * Gotcha * we need either a
        - valid context from `starlette_context` or
        - monkeypatched `builtin` with a global variable defined as hs_user_app_db_path (see `run_user_script` with `builtins` patch for info)


        Returns:
            str: path to user "db"
        """

        if getattr(builtins, "hs_user_app_db_path", False):
            # running from inside user script and using the weirdly set builtins user_id
            return str(self.path_to_usesr_directory / hs_user_app_db_path)
        else:
            # running from inside fastapi and using the user's context
            return str(getattr(context, "hs_user_app_db_path", "main"))

    def get_components(
        self,
    ):
        with shelve.open(self.get_app_db_path()) as app_db:
            return app_db.get("components", OrderedDict())

    def write_components(
        self,
        components,
    ):
        with shelve.open(self.get_app_db_path()) as app_db:
            app_db["components"] = components

    def clear_components(self):
        with shelve.open(self.get_app_db_path()) as app_db:
            app_db["components"] = OrderedDict()

    def schedule_component_refresh(self, component_name):
        with shelve.open(self.get_app_db_path()) as app_db:
            app_db["update_required"] = app_db.get("update_required", set()).union(
                set([component_name])
            )

    def clear_component_refresh_queue(self, component=None, all_component=False):
        with shelve.open(self.get_app_db_path()) as app_db:
            if all_component:
                app_db["update_required"] = set()
            else:
                updates_required = app_db.get("update_required", set())
                updates_required.discard(component)
                app_db["update_required"] = updates_required

    def get_component_refresh_queue(self):
        with shelve.open(self.get_app_db_path()) as app_db:
            return app_db.get("update_required", set())

    def build_fastapi_app(self):
        # Add main html to app
        @self.app.get("/", response_class=HTMLResponse)
        async def root(
            request: Request,
            response: Response,
        ):
            assert context.hs_user_app_db_path
            #
            # since we're starting with a blank page we won't need  a full page reload
            # if this isn't set we get full reload requests from the first user script run (because there are delta's)
            self.clear_component_refresh_queue(all_component=True)

            components = self.get_components()
            response = templates.TemplateResponse(
                "main.html",
                {"request": request, "components": components},
            )
            return response

        @self.app.get("/{component_key}/label", response_class=HTMLResponse)
        async def func_for_component(
            component_key, request: Request, response: Response
        ):
            # lets remove this from our refresh queue as we're processing it
            assert getattr(context, "hs_user_app_db_path", False)
            component_attr = self.get_components()[component_key]
            self.clear_component_refresh_queue(
                component=component_attr["component_key"]
            )
            # Make sure we have the required attributes before passing to Jinja avoids ambigious HTML bugs
            assert component_attr.get("component_key", False) and component_attr.get(
                "label", False
            )

            if component_attr["component_type"] == "Nav":
                headers = {"HX-Retarget": "#hs-nav"}
            else:
                headers = {}

            return HTMLResponse(component_attr["label"], headers=headers)

        @self.app.post("/value_changed/{component_key}")
        async def func_for_component_value_changed(component_key, request: Request):
            """
            Set component with key of query param or form entry to value

            Args:
                request (Request): _description_

            Returns:
                _type_: _description_
            """
            components = self.get_components()
            form_values = await request.form()

            component_value_from_form = form_values.get(component_key, False)
            component_value_from_query_params = request.query_params.get(
                component_key, False
            )
            assert component_value_from_form or component_value_from_query_params
            component_value = (
                component_value_from_form
                if component_value_from_form
                else component_value_from_query_params
            )
            components[component_key]["current_value"] = component_value
            self.write_components(
                components,
            )
            self._queue_user_script_rerun = True
            return PlainTextResponse(
                "success",
                headers={
                    "HX-Reswap": "none",  # we don't want the response to be swapped into the element
                    "HX-Trigger": "get-updated-components",  # we don't want the response to be swapped into the element
                },
            )

    def compile_user_code(self):
        self._queue_user_script_rerun = False
        source_path = self.path_to_user_script
        with open(source_path) as f:
            filebody = f.read()

        # Start: funky stuff #TODO fix
        # GOTCHA: we do some funky stuff here
        # to get the user db path (based on user_id stored in cookie and set as context in FastAPI land) through user space
        # we add a line at the top of the users' code to monkeypatch `hs_user_app_db_path` globally as the current visotors
        # db path
        filebody = f"import builtins \n" + filebody
        filebody = (
            f"""builtins.hs_user_app_db_path = "{getattr(context, 'hs_user_app_db_path', 'error')}" \n"""
            + filebody
        )

        # End: funky stuff

        code = compile(
            filebody,
            source_path,
            mode="exec",
            # Don't inherit any flags or "future" statements.
            flags=0,
            dont_inherit=1,
            # Use the default optimization options.
            optimize=-1,
        )
        exec(
            code,
        )

    def run_user_script(self):
        assert (
            context.hs_user_app_db_path
        )  # we always need the visitor's path before we execute the script so we know where to store the visitors components

        # We do a delta here to if
        # 1) new elements have been added / page layout has changed -> the whole page needs to reload
        # 2) components display's have changed (i.e. a `write` has a new value) -> just that component needs a refresh
        compoennts_before_user_run = self.get_components()
        self.compile_user_code()
        proposed_components_state = self.get_components()
        self.write_components(self.get_components())

        # START: Annoying section #TODO fix this
        # because we're just writing html components into the components dict the delta generator below gets confused and we
        # first need to strip them out - or the page does a full reload every `/update`
        compoennts_before_user_run = dict(
            filter(
                lambda component: HS_HTML_CONSTANT not in component[0],
                compoennts_before_user_run.items(),
            )
        )

        proposed_components_state = dict(
            filter(
                lambda component: HS_HTML_CONSTANT not in component[0],
                proposed_components_state.items(),
            )
        )
        # END: Annoying section

        if not compoennts_before_user_run.keys() == proposed_components_state.keys():
            self.schedule_component_refresh("_full_page")

        else:
            self.clear_component_refresh_queue(component="_full_page")
            for key_before, attr_before in compoennts_before_user_run.items():
                attr_next = proposed_components_state[key_before]
                component_attr_to_trackchanges = ["label"]
                for attr_to_track in component_attr_to_trackchanges:
                    if not attr_before[attr_to_track] == attr_next[attr_to_track]:
                        self.schedule_component_refresh(key_before)


from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware import Middleware

from starlette_context import context, plugins
from starlette_context.middleware import RawContextMiddleware


middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin(),
        ),
    )
]

hs = Hyperstream()