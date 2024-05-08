import cherrypy
from pathlib import Path
from hstream.HSServer import RootServerPathWorld
from typing import Dict

cherrypy.config.update(
    {
        "tools.sessions.on": True,
        "tools.sessions.timeout": 60,  # Timeout is in minutes
        "tools.sessions.locking": "explicit",
        #     'log.screen': False,
        #     'log.access_file': '',
        #     'log.error_file': ''
    }
)

def run_server(file: Path, other_paths: Dict[str, Path] = False, hs_root_path: str = "/"):
    cherrypy.tree.mount(RootServerPathWorld(file), hs_root_path)
    if other_paths:
        for path, handler in other_paths.items():
            cherrypy.tree.mount(handler(), path)
    cherrypy.engine.start()
    cherrypy.engine.block()
