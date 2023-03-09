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
from graphviz import Digraph

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
    dot = Digraph()
    dot.attr('node', shape='record', style='rounded', fontsize='12')
    dot.attr('edge', fontsize='12', color='gray')

    # Finde alle Klassen in der anderen Datei, die von GraphCreatorBase erben
    subclasses = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, module.GraphCreatorBase) and obj != module.GraphCreatorBase:
            subclasses.append(obj)

    if len(subclasses) == 0:
        print("No suitable classes found!")
        raise typer.Abort()

    for subclass in subclasses:  # type: GraphCreatorBase
        for ed_def in subclass._edge_definitions:
            if any(isinstance(item, str) for item in
                   ed_def["from_collections"] + ed_def["to_collections"] + [ed_def["relation"]]):
                print(f"Edge definition contains elements which are defined via String and not as Class!")
                raise typer.Abort()
            for collection in ed_def["from_collections"] + ed_def["to_collections"]:
                collection_name = GraphCreatorBase.get_collection_name(collection)
                dot.node(collection_name, collection_name + "\\n:" + "\\n:".join(collection._fields))

            dot.edge(' '.join([GraphCreatorBase.get_collection_name(m) for m in ed_def["from_collections"]]),
                     ' '.join([GraphCreatorBase.get_collection_name(m) for m in ed_def["to_collections"]]),
                     label=GraphCreatorBase.get_collection_name(ed_def["relation"]) + "\\n:" + "\\n:".join(
                         ed_def["relation"]._fields))
        # Speichere das Diagramm in einer Datei und zeige es im Notebook an
    dot.render('Klassendiagramm', outfile='render.png', format='png', view=False)


@app.command()
def viz():
    from graphviz import Digraph

    # Erstelle eine neue Instanz von Digraph
    dot = Digraph()

    # Füge Knoten hinzu und beschrifte sie mit Klassennamen und Attributen
    dot.node('A', 'Klasse A\\nattr1: int\\nattr2: str')
    dot.node('B', 'Klasse B\\nattr3: float\\nattr4: bool')
    dot.node('C', 'Klasse C\\nattr5: list')

    # Füge Kanten hinzu
    dot.edge('A', 'B')
    dot.edge('B', 'C')
    dot.edge('C', 'A')

    # Zeige das Diagramm an
    dot.view()


if __name__ == "__main__":
    app()
