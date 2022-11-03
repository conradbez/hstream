from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from pathlib import Path
import sys
import uvicorn
import contextlib
import threading
import time

import shelve
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Literal, OrderedDict
# Flow of StreamHTML
# - User script run and each call to sh.write is recorded in a shelve db
# - fast api routes are built of values in shelve
# - initial html is built off shelve (maps to fast api routes)
# - home route added to fast api
#
#  Considerations
# On code changes (fast api handles reload)
templates = Jinja2Templates(directory="templates")
emit = {'server_should_reload': False}


class Hyperstream():

    def __init__(self, clean_reload=False):
        self.app = FastAPI()
        with shelve.open('/Users/conrad/gh/streamhtml/app_db') as app_db:
            if clean_reload:
                print('''
                cleaning
                
                ''')
                app_db['components'] = OrderedDict()
        self._server_should_reload = False
        self._queue_user_script_rerun = True

    def __call__(self):
        """Builds all our paths and returns app so the server (uvicorn) can run the built app

        Returns:
            FastAPI()
        """
        self.build_fastapi_app()
        @self.app.get("/update")
        async def should_components_update(request: Request, response: Response):
            
            with shelve.open('/Users/conrad/gh/streamhtml/app_db') as app_db:
                components = list(app_db.get('update_required', []))
                # response.headers["HX-Trigger"] = ', '.join(components)
                # htmx expect multiple triggers in JSON format - see: https://github.com/bigskysoftware/htmx/issues/1030
                # final form should be {"mywrite":"", "mysecondevent":""}
                import json
                response.headers["HX-Trigger"] = json.dumps({c: "" for c in components})
                print(response.headers["HX-Trigger"])
                # gotcha here is that fastapi transforms any "_" to a "-" in the header values
            return str(response.headers["HX-Trigger"])

        # Add some code to check if the python scrippt should run before we respond
        @self.app.middleware("http")
        async def evaluate_user_code_middleware(request: Request, call_next):
            response = Response("Internal server error", status_code=500)
            try:
                if self._queue_user_script_rerun:
                    # print('calling comile')
                    self.run_user_script(clean_reload=False)
                else:
                    pass
                    # print('code compile skipped')
                response = await call_next(request)
            finally:
                pass
            return response

        return self.app

    def write(self, text: str, key: str = False) -> None:
        """Display test on the users browser

        Args:
            text (str): Text to render

        Returns:
            None
        """
        if not key:
            key = text
        
        return self.build_component(label=text, component_type='Write', key=key)

    def text_input(self, text: str, default_value: str, key:str = None) -> str:
        """Displays text input for user to input text

        Args:
            text (str): label to display to user describing the text input 
            default_value (str): value innitially entered into text box
        Returns:
            str: text inputted by user
        """
        if not key:
            key = text
        
        return self.build_component(label=text, component_type='TextInput', default_value=default_value, key=key)

    def build_component(self, component_type: Literal['write', 'TextInput'], label=None, default_value=None, key=None, **kwargs):
        """Writes a component to the SH front end

        Args:
            label (_type_, optional): Must be ubique within the app. Content to write to the web front end. Defaults to None.
            default_value (_type_, optional): default value the component returns before use enters value - will always be null for text or component where user doesn't input. Defaults to None.
        """
        component_key = key if key else label   # if key isn't provided we assume label is unique
        assert not '_' in component_key,  "please don't use underscores in keys"  # we use headers to update compoennts by key but headers don't like underscores
        with shelve.open('/Users/conrad/gh/streamhtml/app_db') as app_db:
            components = app_db['components']
            if not components.get(component_key, False):
                # if we don't have this component stored initialise it
                components[component_key] = {
                    # these values shouldn't change between reruns so we set them here on initialisation
                    'current_value': default_value,
                    'component_key': component_key,
                    'component_type': component_type,
                }
            
            if not components[component_key].get('label') == label: # TODO add kwargs
                # schedule component for update
                app_db ['update_required']= app_db.get('update_required', set()).union(set([component_key]))

            components[component_key].update({
                # these values can change between reruns (i.e. text input is outputted to a write component)
                'label': label,
            })
            
            app_db['components'] = components
        return components[component_key]['current_value']

    def build_fastapi_app(self):
        with shelve.open('/Users/conrad/gh/streamhtml/app_db') as app_db:
            components = app_db['components']
            # give each component a route on fast api app
            for component_key, component_attr in app_db['components'].items():
                # Return the items label
                self.app.get(f'/{component_attr["component_key"]}/label',
                             response_class=HTMLResponse)(self.function_generator_component(component_attr))
                self.app.post(f'/{component_attr["component_key"]}/value_changed',
                              response_class=HTMLResponse)(self.function_generator_value_changed(component_attr))

        # Add main html to app
        @self.app.get("/", response_class=HTMLResponse)
        async def root(request: Request,):
            with shelve.open('/Users/conrad/gh/streamhtml/app_db') as app_db:
                return templates.TemplateResponse("main.html", {"request": request, "components": app_db['components']})

    def function_generator_component(self, component_attr):
        """Generates function for attaching to FastAPI to render the initial view of the element

        Args:
            component_attr (_type_): _description_

        Returns:
            _type_: _description_
        """
        component_key = component_attr['component_key']
        # `func_for_component` is wrapped like this because se rely on `component_attr` to be "stored" in this function
        # so each component is not overriden by the component that comes after it
        async def func_for_component(request: Request,):
            # Make sure we have the required attributes before passing to Jinja avoids ambigious HTML bugs
            with shelve.open('/Users/conrad/gh/streamhtml/app_db') as app_db:
                
                update_required_set = app_db.get('update_required', set())
                try:
                    update_required_set.remove(component_key)
                except:
                    pass
                
                app_db['update_required'] = update_required_set
                
                assert component_attr.get(
                    'component_key', False) and component_attr.get('label', False)
                if app_db['components'][component_key]['component_type'] == 'TextInput':
                    return templates.TemplateResponse("./components/TextInput.html", {"request": request, "component_attr": component_attr})
                elif app_db['components'][component_key]['component_type'] == 'Write':
                    return '<p>' + app_db['components'][component_key]['label'] + '</p>'
        return func_for_component

    def function_generator_value_changed(self, component_attr):
        """Generates function for attaching to FastAPI to accept user inputs to the component and queues a user script rerun
        """
        component_key = component_attr['component_key']
        async def func_for_component(request: Request, ):
            with shelve.open('/Users/conrad/gh/streamhtml/app_db') as app_db:
                components = app_db['components']
                form_values = await request.form()
                component_value = form_values[component_key]
                components[component_key]['current_value'] = component_value
                app_db['components'] = components
            self._queue_user_script_rerun = True
            print('here at _queue setting')

            return "success"

        return func_for_component

    def compile_user_code(self):
        self._queue_user_script_rerun = False
        source_path = Path('/Users/conrad/gh/streamhtml/main.py')
        with open(source_path) as f:
            filebody = f.read()
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
        exec(code)

        print('code compile')
        with shelve.open('/Users/conrad/gh/streamhtml/app_db') as app_db:
            print(app_db['components'], 'components after compilation')

    def run_user_script(self, clean_reload=True):
        self.__init__(clean_reload=clean_reload)
        self.compile_user_code()
        self.build_fastapi_app()
        self._server_should_reload = True

class UserScriptEventHandler(LoggingEventHandler):
    def dispatch(self, event):
        print('user file changed')
        global app_factory
        global hs
        hs.run_user_script(clean_reload=True)
        print('''User file changed''')

class Server(uvicorn.Server):
    # https://stackoverflow.com/questions/61577643/python-how-to-use-fastapi-and-uvicorn-run-without-blocking-the-thread
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


hs = Hyperstream(clean_reload=True)
hs.run_user_script(clean_reload=True)

if __name__ == '__main__':

    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = UserScriptEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            config = uvicorn.Config(
                "hyperstream:hs",
                host="127.0.0.1",
                port=8000,
                reload='True',
                reload_dirs=['/Users/conrad/gh/streamhtml'],
                reload_includes=['*'],
                factory=True
            )

            server = Server(config=config)

            with server.run_in_thread():
                # stay in loop unless the server needs to exit
                while not hs._server_should_reload:
                    time.sleep(1)
                hs._server_should_reload = False

    except KeyboardInterrupt:
        observer.stop()
    observer.join()
