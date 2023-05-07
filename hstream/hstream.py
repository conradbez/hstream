from random import randint
from pathlib import Path
import sys
import builtins
import shelve
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from typing import OrderedDict
import os
from yattag import Doc
from .components import Components
from jinja2 import Environment, FileSystemLoader

# Vocab
# User: Person using this library to build web apps
# Visitor: person visiting the user's web app
# Component: HStream element that displays an output to the visitor based on user scipt (i.e. hs.write)
# and optionally takes and input from the visitor, feeding it back to the user's script (i.e. hs.text_input)

# Flow of StreamHTML
# - Visitor loads `/` and assigned a unique id
# - User script runs, with hs.* components returning defaults and building html
# - Content is loaded with html morph into the visitors browser
# - Visitor interacts with website, updates a input triggeting a `/value_changed` and a page refetch
# - hs.input component's value updated in the user's db (based on user id) and script rerun with this value
# - html is served and htmx's morph inserts updated html
#
# Considerations
# - On code changes during local development uvicorn handles reload
# - Nav is dynamically moved out of main content area with hyperscript
templates_path = Path(__file__).parent / "templates"

environment = Environment(loader=FileSystemLoader(templates_path))

class Hstream(Components):
    def __init__(self, development_mode = True):
        self.development_mode = development_mode
        self.app = FastAPI(debug=self.development_mode, middleware=middleware)
        self.path_to_user_script = Path(os.getcwd()) / Path(sys.argv[1])
        assert (
            self.path_to_user_script
        ), "please make sure the first argument is the script file location"
        self.path_to_user_directory = Path(os.getcwd())
        self.path_to_app_db = Path(os.getcwd()) / "app_db"

        # on init we start fresh
        self.clear_components()
        self.stylesheet_href = "https://unpkg.com/mvp.css@1.12/mvp.css"
        self.doc, self.tag, self.text = Doc().tagtext()

    def __call__(self):
        """Builds all our paths and returns app so the server (uvicorn) can run the built app

        Returns:
            FastAPI()
        """
        self.build_fastapi_app()

        # Assign user_id if it doesn't exist, 
        # setup db and 
        # check if the python script should run before we respond
        @self.app.middleware("http")
        async def evaluate_user_code_middleware(
            request: Request,
            call_next,
        ):
            response = Response("Internal server error", status_code=500)
            hs_user_id = request.cookies.get("hs_user_id", False)
            if not hs_user_id:
                hs_user_id = str(randint(100000, 1000000))
                context.hs_user_app_db_path = (
                    self.path_to_user_directory / "hs_data" / str(hs_user_id)
                )
            else:
                context.hs_user_app_db_path = (
                    self.path_to_user_directory / "hs_data" / str(hs_user_id)
                )
            if request.url.path == "/":
                # If the user is coming to the root or reloading the page we'll assume 
                # they don't want to use previous component values set by the user so we 
                # clear them
                self.clear_components()
            if request.url.path == "/poll_root":
                # If the user is coming to the root or reloading the page we'll assume 
                # they don't want to use previous component values set by the user so we 
                # clear them
                self.clear_components()

            assert context.hs_user_app_db_path
            response = await call_next(request)

            response.set_cookie("hs_user_id", hs_user_id)
            return response

        return self.app

    def list_css_frameworks(self):
        """
        Returns css framework names and urls for the users convenience - script used to generate files in css_frameworks.py

        ```
        from bs4 import BeautifulSoup
        import requests
        r = requests.get("https://cdn.jsdelivr.net/gh/dohliam/dropin-minimal-css/src/")
        soup = BeautifulSoup(r.text)
        table = soup.find('table')
        rows = {}
        base_url = "https://cdn.jsdelivr.net"
        for i, row in enumerate(table.find_all('tr')):
            rows[row.find('td').text.strip()] = base_url + row.find('a').get('href')
        rows = rows[1:] # remove the table header
        ```
        """

        from .css_frameworks import css_frameworks
        return css_frameworks
        

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
            path = Path(self.path_to_user_directory / "hs_data" / hs_user_app_db_path)

        else:
            # running from inside fastapi and using the user's context
            path = Path(
                getattr(
                    context,  # uses FastAPI's request wide context
                    "hs_user_app_db_path",  # get the hs_user_app_db_path attribute set on request based on user cookie
                    # for run's without a user (I think this just happen on the first run)
                    # there is no cookie and we just fail gracefully to a common db
                    # this might not be necessary and could maybe just go to /dev/null
                    self.path_to_user_directory / "hs_data" / "main.db",
                )
            )
            path.parent.mkdir(exist_ok=True)
        return str(path)  # we cast this to string because `shelve` doesn't like paths

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

    def build_fastapi_app(self):
        # Add main html to app
        @self.app.get("/", response_class=HTMLResponse)
        async def root(
            request: Request,
            response: Response,
        ):
            assert context.hs_user_app_db_path
            return HTMLResponse(
                environment.get_template("main.html").render(
                    {
                        "stylesheet": self.stylesheet_href,
                    }
                )
            )

        @self.app.get("/content", response_class=HTMLResponse)
        async def content(
            request: Request,
            response: Response,
        ):
            assert context.hs_user_app_db_path
            #
            # since we're starting with a blank page we won't need  a full page reload
            # if this isn't set we get full reload requests from the first user script run (because there are delta's)
            html = self.run_user_script()
            return HTMLResponse(html)

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
            try:
                components[component_key] = component_value
            except KeyError:
                print(
                    f"compoennt {component_key} doesnt exist yet but tried to set a value"
                )
                components[component_key] = component_value

            self.write_components(
                components,
            )
            response = HTMLResponse(
                "success",
                headers={
                    "HX-Trigger": "update_content_event",
                },
            )
            return response

    def compile_user_code(self):
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
        """
        Runs the user script, (which fetches previous user values from shelve) 
        and returns the html compiled during the run
        """
        assert (
            context.hs_user_app_db_path
        )  # we always need the visitor's path before we execute the script so we know where to store the visitors components

        self.doc, self.tag, self.text = Doc().tagtext()

        self.compile_user_code()
        return self.doc.getvalue()


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

hs = Hstream()


if __name__ == "__main__":
    from .runner import run

    run()
