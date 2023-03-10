import importlib
import inspect
import os
import platform
import zipfile
from pathlib import Path
from subprocess import PIPE, run

import typer
from pyvis.network import Network
from rich import print
from rich.console import Console
from slugify import slugify

from cag.framework import GraphCreatorBase

console = Console()
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
def visualize(python_file: Path) -> Path:
    """
    Visualize the graph of the collections and relations defined in a Python file.

    Parameters:
    -----------
    python_file : Path
        The path of the Python file containing a GraphCreatorBase class that define the collections
        and relations to be visualized.

    Raises:
    -------
    typer.Abort:
        If the specified `python_file` does not exist or is not a file.

   Returns:
    --------
    Path
        The path of the HTML file containing the generated graph.
        The function saves the generated graph to an HTML file and prints the path of the file.
    """
    if not python_file.exists():
        print(f"{python_file} not found!")
        raise typer.Abort()
    if not python_file.is_file():
        print(f"{python_file} is not a file")
        raise typer.Abort()
    spec = importlib.util.spec_from_file_location(
        python_file.stem, python_file
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    net = Network(height="750px", width="100%")
    net.barnes_hut()

    subclasses = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if (
            issubclass(obj, module.GraphCreatorBase)
            and obj != module.GraphCreatorBase
        ):
            subclasses.append(obj)

    if len(subclasses) == 0:
        print("No suitable classes found!")
        raise typer.Abort()
    with console.status("[bold green]Working...") as status:
        for subclass in subclasses:  # type: GraphCreatorBase
            for ed_def in subclass._edge_definitions:
                for collection in set(
                    ed_def["from_collections"] + ed_def["to_collections"]
                ):
                    collection_name = GraphCreatorBase.get_collection_name(
                        collection
                    )
                    net.add_node(collection_name, label=collection_name)
                    console.log(f"Process {collection}")

                from_collections = [
                    GraphCreatorBase.get_collection_name(m)
                    for m in ed_def["from_collections"]
                ]
                to_collections = [
                    GraphCreatorBase.get_collection_name(m)
                    for m in ed_def["to_collections"]
                ]
                relation_name = GraphCreatorBase.get_collection_name(
                    ed_def["relation"]
                )
                net.add_edge(
                    *from_collections, *to_collections, label=relation_name
                )

        diagram_file = python_file.parent.joinpath(
            python_file.stem + "_diagram.html"
        )
        status.update("Save file")
        net.save_graph(str(diagram_file))
    print(f"File saved to {diagram_file}")
    return diagram_file


if __name__ == "__main__":
    app()
