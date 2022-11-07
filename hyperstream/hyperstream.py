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
import os
from yattag import Doc

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
        self.path_to_user_script = Path(os.getcwd()) / Path(sys.argv[1])
        self.path_to_usesr_directory = Path(os.getcwd())
        self.path_to_app_db = Path(os.getcwd()) / 'app_db'
        self._server_should_reload = False
        self._queue_user_script_rerun = True
    
        if clean_reload:
            self.write_components(OrderedDict())

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
                # see if we need to do a full refresh (usually if content is generated inside a conditional value based on hs)
                if '_full_page' in components:
                    response.headers["HX-Refresh"] = 'true'
                    return str(response.headers["HX-Refresh"])
                else:
                    # response.headers["HX-Trigger"] = ', '.join(components)
                    # htmx expect multiple triggers in JSON format - see: https://github.com/bigskysoftware/htmx/issues/1030
                    # final form should be {"mywrite":"", "mysecondevent":""}
                    import json
                    response.headers["HX-Trigger"] = json.dumps({c: "" for c in components})
                    # gotcha here is that fastapi transforms any "_" to a "-" in the header values
                    return str(response.headers["HX-Trigger"])

        # Add some code to check if the python scrippt should run before we respond
        @self.app.middleware("http")
        async def evaluate_user_code_middleware(request: Request, call_next):
            response = Response("Internal server error", status_code=500)
            try:
                if self._queue_user_script_rerun:
                    self.run_user_script(clean_reload=False)
                else:
                    pass

                response = await call_next(request)
            finally:
                pass
            return response

        return self.app

    def get_components(self):
        with shelve.open(str(self.path_to_app_db)) as app_db:
            return app_db['components']

    def write_components(self, components):
        with shelve.open(str(self.path_to_app_db)) as app_db:
            app_db['components'] = components

    def schedule_component_refresh(self, component_name):
        with shelve.open(str(self.path_to_app_db)) as app_db:
            app_db['update_required']= app_db.get('update_required', set()).union(set([component_name]))

    def clear_component_refresh_queue():
        with shelve.open(str(self.path_to_app_db)) as app_db:
            app_db['update_required']= set()

    def write(self, text: str, key: str = False) -> None:
        """Display test on the users browser

        Args:
            text (str): Text to render

        Returns:
            None
        """
        if not key:
            key = text
        
        return self.build_component(label=text, component_type='Write', key=key, )


    def markdown(self, text: str, key: str = False) -> None:
        if not key:
            key = text
        
        return self.build_component(label=text, component_type='Markdown', key=key, )


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
    
    def slider(self, label: str, minValue:int, maxValue:int, default_value: int, key:str = None) -> str:
        """
        """
        if not key:
            key = label
        kwargs = {
            'minValue': minValue,
            'maxValue': maxValue,

        }
        return self.build_component(label=label, component_type='Slider', default_value=default_value, key=key, **kwargs)

    def nav(self, label: list[str], default_value, key,):
        if not key:
                key = label
        label
        kwargs = {}

        return self.build_component(label=label, component_type='Nav', default_value=default_value, key=key, **kwargs)


    def h1(self, text: str, key:str = None) -> str:
        if not key:
            key = text
        return self.build_component(label=text, component_type='h1', default_value=None, key=key)

    def pyplot(self, fig, key:str = None) -> None:
        """Displays matplotlib plot to user

        Args:
            fig (matplotlib.figure.Figure): label to display to user describing the text input 
        Returns:
            str: text inputted by user


        Example:
            import matplotlib.pyplot as plt
            import numpy as np
            x = np.arange(0,4*np.pi,0.1)   # start,stop,step
            y = np.sin(x) * float(sine_height)
            fig, ax = plt.subplots()
            ax.plot(x,y)
            hs.pyplot(fig, key='myplot')
        """

        from base64 import b64encode
        import io
        my_stringIObytes = io.BytesIO()
        fig.savefig(my_stringIObytes, format='png')
        my_stringIObytes.seek(0)
        my_base64_jpgData = b64encode(my_stringIObytes.read())
        my_base64_jpgData = my_base64_jpgData.decode("utf-8")    
        return self.build_component(label=my_base64_jpgData, component_type='Image', default_value=None, key=key)
        
    def build_component(self, component_type: Literal['write', 'TextInput', 'Image'], label=None, default_value=None, key=None, **kwargs):
        """Writes a component to the SH front end

        Args:
            label (_type_, optional): Must be ubique within the app. Content to write to the web front end. Defaults to None.
            default_value (_type_, optional): default value the component returns before use enters value - will always be null for text or component where user doesn't input. Defaults to None.
        """        
        if key:
            component_key = key 
        else:
             # if key isn't provided we assume label is unique
            component_key = ''.join(x for x in label if x.isalpha() or x.isnumeric())
        assert not '_' in component_key,  "please don't use underscores in keys"  # we use headers to update compoennts by key but headers don't like underscores
        components = self.get_components()
        if not components.get(component_key, False):
            # if we don't have this component stored initialise it
            components[component_key] = {
                # these values shouldn't change between reruns so we set them here on initialisation
                'current_value': default_value,
                'component_key': component_key,
                'component_type': component_type,
            }
            # and set the page to reload in full since this new component won't have a place in the original dom
            print('queue full page reload')
            self.schedule_component_refresh('_full_page')

        if not components[component_key].get('label') == label:
            # schedule component for update
            self.schedule_component_refresh(component_key)

        components[component_key].update({
            # these values can change between reruns (i.e. text input is outputted to a write component)
            'label': label,
        })
        if kwargs:
            components[component_key].update(kwargs)
        self.write_components(components)
        return components[component_key]['current_value']

    def build_fastapi_app(self):
        with shelve.open(str(self.path_to_app_db)) as app_db:
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
            with shelve.open(str(self.path_to_app_db)) as app_db:
                return templates.TemplateResponse("main.html", {"request": request, "components": app_db['components']})

    def function_generator_component(self, component_attr):
        """Generates function for attaching to FastAPI to render the initial view of the element

        Args:
            component_attr (_type_): _description_

        Returns:
            _type_: _description_
        """
        component_key = component_attr['component_key']
        
        # `func_for_component` is wrapped like this because se rely on `component_key` to be "stored" in this function after initialization
        # so each component is not overriden by the component that comes after it
        async def func_for_component(request: Request, response: Response):
            doc, tag, text = Doc().tagtext()
            # Make sure we have the required attributes before passing to Jinja avoids ambigious HTML bugs
            with shelve.open(str(self.path_to_app_db)) as app_db:
                update_required_set = app_db.get('update_required', set())
                try:
                    update_required_set.remove(component_key)
                except:
                    pass  
                app_db['update_required'] = update_required_set
            component_attr = self.get_components()[component_key]
            assert component_attr.get(
                'component_key', False) and component_attr.get('label', False)
            if component_attr['component_type'] == 'TextInput':
                with tag('label'):
                    text(component_attr['label'])
                with tag('input', 
                    ('name', component_key),
                    ('hx-post', f"/{component_key}/value_changed"),
                    ('hx-trigger',"keyup changed"),
                    ('type', "text"),
                    ('value',component_attr['current_value']),
                    ):
                    text(component_attr['label'])
                return doc.getvalue()
            elif component_attr['component_type'] == 'Write':
                with tag('p'):
                    text(component_attr['label'])
                return doc.getvalue()
            elif component_attr['component_type'] == 'Image':
                with tag('img',
                    ('src', f"data:image/png;base64,{component_attr['label']}"),
                    ('alt', 'Graph'),
                ):
                    text('')
            elif component_attr['component_type'] == 'Slider':
                with tag('input',
                    ('name', component_key),
                    ('type', 'range'),
                    ('value',component_attr['current_value']),
                    ('min', component_attr['minValue']),
                    ('max', component_attr['maxValue']),
                    ('hx-post', f"/{component_key}/value_changed"),
                    ):
                    text('')
                return doc.getvalue()
            
            elif component_attr['component_type'] == 'Nav':
                headers = {'HX-Retarget': "#hs-nav"} 
                headers=headers
                # with tag('nav',): 
                for item in component_attr['label']:
                    with tag('ul'):
                        with tag('li',):
                            with tag('a',
                                ('hx-post', f"/{component_key}/value_changed?{component_key}={item}"),
                            ):
                                text(str(item))
                return HTMLResponse(doc.getvalue(), headers=headers)
            elif component_attr['component_type'] == 'h1':
                with tag('h1',):
                    text(component_attr['label'])
                return doc.getvalue()
                
            elif component_attr['component_type'] == 'Markdown':
                import markdown
                html = markdown.markdown(component_attr['label'])
                return HTMLResponse(html)
        return func_for_component

    def function_generator_value_changed(self, component_attr):
        """Generates function for attaching to FastAPI to accept user inputs to the component and queues a user script rerun
        """
        component_key = component_attr['component_key']
        async def func_for_component(request: Request, ):
            """Set component with key of query param or form entry to value

            Args:
                request (Request): _description_

            Returns:
                _type_: _description_
            """
            with shelve.open(str(self.path_to_app_db)) as app_db:
                components = app_db['components']
                form_values = await request.form()

                component_value_from_form = form_values.get(component_key, False)
                component_value_from_query_params = request.query_params.get(component_key, False)
                assert component_value_from_form or component_value_from_query_params
                component_value = component_value_from_form if component_value_from_form else component_value_from_query_params
                print('component value', component_value)
                components[component_key]['current_value'] = component_value
                app_db['components'] = components
            self._queue_user_script_rerun = True

            return PlainTextResponse(
                "success", 
                headers={
                    'HX-Reswap':'none', # we don't want the response to be swapped into the element
                    'HX-Trigger': 'get-updated-components' # we don't want the response to be swapped into the element
                    }
                )

        return func_for_component

    def compile_user_code(self):
        self._queue_user_script_rerun = False
        source_path = self.path_to_user_script
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

    def run_user_script(self, clean_reload=True):
        self.__init__(clean_reload=clean_reload)
        self.compile_user_code()
        self.build_fastapi_app()
        self._server_should_reload = True
