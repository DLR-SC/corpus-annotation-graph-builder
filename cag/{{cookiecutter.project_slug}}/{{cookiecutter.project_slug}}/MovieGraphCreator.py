from conf import config
from graph import FilmActorGraph

if __name__ == "__main__":
    """
    Main script to create a FilmActorGraph and its view.

    Args:
        None

    Returns:
        None
    """
    gc = FilmActorGraph(
        corpus_file_or_dir="./data/sample_data.json",
        initialize=True,
        load_generic_graph=False,
        conf=config,
    )
    gc.create_view()
