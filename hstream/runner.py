import os
import uvicorn
from uvicorn import Server
import click
from pathlib import Path

@click.command()
@click.argument("user_filename")
@click.option("--port", default=8080, help="Port to run the server")
@click.option(
    "--host",
    default="127.0.0.1",
)
def run(user_filename, port, host):
    user_file_path = os.getcwd() / Path(user_filename)
    # lets convert the user input to folder1.folder2.filename:hs

    if Path(user_filename).parent == Path("."):
        # if we're in the same folder as the file, we use this format
        uvicorn_style_path_to_file = user_file_path.stem+':hs'# we're already speciffying the folder in the app_dir below
        user_file_path = Path.cwd() / user_filename
    else:
        # if the users folder is in a nested directory, we use this format
        uvicorn_style_path_to_file = str(Path(user_filename).parent).replace("/", ".") + '.'+user_file_path.stem+':hs'
    
    print(f"activating app: {uvicorn_style_path_to_file}")
    uvicorn.run(
        uvicorn_style_path_to_file,
        host=host,
        port=port,
        reload="True",
        factory=True,
        app_dir=user_file_path.parent,
        reload_dirs=[user_file_path.parent],
    )

if __name__ == "__main__":
    run()
