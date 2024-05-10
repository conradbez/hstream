# run with `python example_server.py`

from hstream.run import run_server
import cherrypy

class TestServerPathWorld(object):
    @cherrypy.expose
    def index(
        self,
    ):
        return """
        <h1>🚀 Custom path</h1>
        HStream easily mount on another path to 
        make it easy when you outgrow our framework
        """

run_server(
    "example.py",
    {"/custom": TestServerPathWorld},
)
