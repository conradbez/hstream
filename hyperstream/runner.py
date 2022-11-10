import os
import uvicorn
from uvicorn import Server
import click
from pathlib import Path

@click.command()
@click.argument('user_filename')
def run(user_filename='main'):
    print(user_filename)    
    uvicorn.run(
        f"{Path(user_filename).stem}:hs",
        host="127.0.0.1",
        port=8083,
        reload="True",
        factory=True,
        app_dir=os.getcwd(),
        reload_dirs=[os.getcwd()],
    )

if __name__ == "__main__":
    run()