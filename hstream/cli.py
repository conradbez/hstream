import click
from hstream.run import run_server
from pathlib import Path


@click.group()
def cli():
    pass

@click.command()
@click.argument("file", type=click.Path())
def run(file=Path("./app.py")):
    click.echo('Running server...')
    file = Path(file)
    run_server(file)

@click.command()
def init():
    import urllib.request
    url = "https://raw.githubusercontent.com/conradbez/hstream/main/demo/example.py"
    response = urllib.request.urlopen(url)
    content = response.read().decode()
    if example := Path("example.py"):
        if example.exists():
            click.echo(click.style(f"example.py already exists", fg='red'), err=True,)
            return
    with open("example.py", "w") as f:
        f.write(content)

    click.echo('Initialized example.py')
    click.echo('Now run:')
    click.echo(click.style(f"     hstream run example.py", fg='green'))
    # click.echo('        hstream run example.py', color='green')

cli.add_command(run)
cli.add_command(init)

if __name__ == "__main__":
    cli()