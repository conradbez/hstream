from pathlib import Path
import importlib
from typing import Dict
import os
import hstream


def run_server(
    file: Path, other_paths: Dict[str, Path] = False, hs_root_path: str = "/"
):
    path_to_hstream_dir = os.path.dirname(os.path.abspath(hstream.__file__))
    os.environ["HS_FILE_TO_RUN"] = str(file)
    os.system(f"python {path_to_hstream_dir}/django_server/manage.py runserver")
