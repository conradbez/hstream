# run with `python example_server.py`

from hstream.run import run_server
import cherrypy


class TestServerPathWorld(object):
    @cherrypy.expose
    def index(
        self,
    ):
        return "Custom application"


run_server(
    "example.py",
    {"/test": TestServerPathWorld},
)
