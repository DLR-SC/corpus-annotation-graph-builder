import ast
import importlib
import inspect
import os
import platform
import zipfile
from pathlib import Path
from subprocess import PIPE, run

import typer
from slugify import slugify
from rich import print

from cag.framework import GraphCreatorBase

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
    name = setup_project_name()
    project_dir = setup_project_dir(name)
    path = Path(os.path.dirname(__file__))  # get path where the module is
    with zipfile.ZipFile(
            f"{path.joinpath('cag_sample_project.zip')}", "r"
    ) as zip_ref:
        zip_ref.extractall(project_dir)
    print(f"[green] Creating scaffold in {project_dir}[/green]")


@app.command()
def visualize(python_file: Path):
    if not python_file.exists():
        print(f"{python_file} not found!")
        raise typer.Abort()
    if not python_file.is_file():
        print(f"{python_file} is not a file")
        raise typer.Abort()
    # Lade die andere Datei als Modul
    spec = importlib.util.spec_from_file_location(python_file.stem, python_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Finde alle Klassen in der anderen Datei, die von GraphCreatorBase erben
    subclasses = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, module.GraphCreatorBase) and obj != module.GraphCreatorBase:
            subclasses.append(obj)

    if len(subclasses) == 0:
        print("No suitable classes found!")
        raise typer.Abort()

    for subclass in subclasses:  # type: GraphCreatorBase
        print(subclass._edge_definitions)


if __name__ == "__main__":
    app()
