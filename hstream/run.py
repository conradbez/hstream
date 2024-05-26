import os
from pathlib import Path
from typing import Dict

import hstream


def run_server(
    file: Path, other_paths: Dict[str, Path] = False, hs_root_path: str = "/"
):
    path_to_hstream_dir = os.path.dirname(os.path.abspath(hstream.__file__))

    os.system(f'python "{path_to_hstream_dir}/django_server/manage.py" migrate')
    os.environ["HS_FILE_TO_RUN"] = str(file)
    command = f'python "{path_to_hstream_dir}/django_server/manage.py" runserver'
    if os.environ.get("PORT", False):
        print(f"found port in env, using port {os.environ['PORT']}")
        command += f" 0.0.0.0:{os.environ['PORT']}"
    os.system(command)
