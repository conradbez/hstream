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
    uvicorn.run(
        f"{Path(user_filename).stem}:hs",
        host=host,
        port=port,
        reload="True",
        factory=True,
        app_dir=os.getcwd(),
        reload_dirs=[os.getcwd()],
    )



if __name__ == "__main__":
    run()
