import click
import os
from pathlib import Path
from app import run_app
import time

@click.command()
@click.argument('path', required=False, type=click.Path(exists=True))
def main(path):
    if path is None:
        # No path provided, use current directory
        run_app(str(Path.cwd()))
    else:
        path_obj = Path(path)
        # Directory provided - open app in that directory
        click.echo(f"Opening file editor in directory: {path}")
        run_app(str(path_obj))

if __name__ == '__main__':
    main()