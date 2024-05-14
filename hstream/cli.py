import os
import shutil
from pathlib import Path

import click

import hstream
from hstream.run import run_server


@click.group()
def cli():
    pass


@click.command()
@click.argument(
    "file",
    type=click.Path(),
)
def eject(file=Path("./app.py")):
    click.echo("Ejecting a django server...")
    file = Path(file)
    path_to_hstream_dir = os.path.dirname(os.path.abspath(hstream.__file__))
    django_server = Path(path_to_hstream_dir) / "django_server"
    destination_dir = "./"

    for item in os.listdir(django_server):
        s = os.path.join(django_server, item)
        d = os.path.join(destination_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    hs_view_contents = open("./hs/views.py", "r").read()
    hs_view_contents = hs_view_contents.replace(
        'os.environ["HS_FILE_TO_RUN"]', f'"{str(file)}"'
    )
    with open("./hs/views.py", "w") as f:
        f.write(hs_view_contents)

    click.echo("Django server ejected successfully.")
    click.echo("You can now run:.")
    click.echo(click.style("     python manage.py runserver", fg="green"))


@click.command()
@click.argument(
    "file",
    type=click.Path(),
)
def run(file=Path("./app.py")):
    click.echo("Running server...")
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
            click.echo(
                click.style("example.py already exists", fg="red"),
                err=True,
            )
            return
    with open("example.py", "w") as f:
        f.write(content)

    click.echo("Initialized example.py")
    click.echo("Now run:")
    click.echo(click.style("     hstream run example.py", fg="green"))


@click.command()
@click.argument("file", default=False)
def deploy(file=False):
    if not file:
        file = click.prompt(
            "Enter the file containing the hstream app you want to deploy ",
            default="./app",
        )
    if Path("Dockerfile").exists():
        click.echo(
            click.style("Dockerfile already exist - can't over write", fg="red"),
            err=True,
        )
        return
    else:
        with open("Dockerfile", "w") as f:
            f.write(DOCKERFILE.format(filename=file))

    click.echo("Dockerfile created successfully")
    click.echo("""We recommend deploying on Railway using the below""")
    click.echo(
        """If you don't have an account create one (free):
                https://railway.app?referralCode=1OLHEp"""
    )
    click.echo(
        click.style(
            f"""
                {"brew install railway" if shutil.which("brew") else "Follow: https://docs.railway.app/guides/cli for install railway cli"}
                railway login
                railway link
                railway up""",
            fg="green",
        )
    )


cli.add_command(eject)
cli.add_command(deploy)
cli.add_command(run)
cli.add_command(init)


if __name__ == "__main__":
    cli()


DOCKERFILE = """
FROM python:3.11-slim
WORKDIR /code
RUN pip install --upgrade pip
RUN pip install hstream
# RUN pip install -r requirements.txt # uncomment if you have a requirements.txt
# COPY requirements.txt /code/
COPY . /code/
CMD hstream run {filename}
"""
