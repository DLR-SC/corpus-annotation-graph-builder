import os
import platform
import subprocess
import sys
import venv
import zipfile
from pathlib import Path
from subprocess import PIPE, run

import typer
from slugify import slugify
from rich import print

app = typer.Typer()


def setup_project_name():
    return typer.prompt("Enter desired project name", type=str)


def setup_project_dir(project_name: str):
    cwd = os.getcwd()
    project_dir = Path(cwd).joinpath(slugify(project_name))
    if project_dir.exists():
        print(f"Aborting. {project_dir} already existent!")
        raise typer.Abort()
    if not typer.confirm(
            f"Set {project_dir} as the project directory. Is this correct?",
            default=True,
    ):
        print("Aborting...")
        raise typer.Abort()
    print(f"Creating {project_name}")
    project_dir.mkdir()
    return project_dir


@app.command()
def show_info():
    """
    Use this info when opening issues!
    """
    command = ["pip", "show", "cag"]
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print(f"Package info\n{result.stdout}")
    print(10 * "=")
    print(f"Python version {platform.python_version()}")
    print(10 * "=")
    print(f"OS: {platform.platform(aliased=True)}")


@app.command()
def start_project():
    """
    Creates project scaffold to get you started
    """
    from cookiecutter.main import cookiecutter
    cwd = Path.cwd()
    cag_install_dir = str(Path(__file__).parent) + "/"
    project_dir = Path(cookiecutter(cag_install_dir, output_dir=cwd))
    if typer.confirm(f"Create new virtual environment under {project_dir.joinpath('venv')}", default=True):
        requirements_file = project_dir.joinpath('requirements.txt')
        venv.create(project_dir.joinpath('venv'), with_pip=True)
        subprocess.check_call([project_dir.joinpath('venv/bin/python'), '-m', 'pip', 'install', '-r', requirements_file])

if __name__ == "__main__":
    app()
