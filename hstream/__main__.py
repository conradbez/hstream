from pathlib import Path
import click
from hstream.run import run_server


@click.command()
@click.argument("file", type=click.Path())
def start_server(file=Path("./app.py")):
    file = Path(file)
    run_server(file)


if __name__ == "__main__":
    start_server()
