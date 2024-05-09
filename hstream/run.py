import cherrypy
from pathlib import Path
from hstream.HSServer import RootServerPathWorld
from typing import Dict

config = {
    "tools.sessions.on": True,
    "tools.sessions.timeout": 60,  # Timeout is in minutes
    "tools.sessions.locking": "explicit",
    "log.screen": True,
    #  'log.access_file': '',
    #  'log.error_file': ''
}

cherrypy.config.update(config)

def run_server(
    file: Path, other_paths: Dict[str, Path] = False, hs_root_path: str = "/"
):
    cherrypy.tree.mount(RootServerPathWorld(file), hs_root_path, config={"/": config})
    
    if other_paths:
        for path, handler in other_paths.items():
            cherrypy.tree.mount(handler(), path, config={"/": config})
    cherrypy.engine.start()
    cherrypy.engine.block()
