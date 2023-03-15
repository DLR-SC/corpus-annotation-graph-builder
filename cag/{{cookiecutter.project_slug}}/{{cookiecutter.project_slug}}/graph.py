import json

from cag.framework import GraphCreatorBase

from edges import PlayedIn, Directed
from nodes import Actor, Movie, Director
from cag.view_wrapper.arango_analyzer import ArangoAnalyzer, AnalyzerList
from cag.view_wrapper.link import Link, Field as ViewField
from cag.view_wrapper.view import View


class FilmActorGraph(GraphCreatorBase):
    """
    A class to create a graph describing the relationships between actors and movies.

    Attributes:
        _name (str): The name of the graph.
        _description (str): A description of the graph.
        _edge_definitions (list): A list of edge definitions for the graph.

    Methods:
        init_graph() -> None:
            Initializes the graph by reading data from a JSON file and creating nodes and edges.

        create_view() -> None:
            Creates a view for the movies collection with fuzzy search and tokenization analyzers.
    """

    _name = "FilmActorGraph"
    _description = "Graph describing relations between Actors and movies"

    _edge_definitions = [
        {
            "relation": PlayedIn,
            "from_collections": [Actor],
            "to_collections": [Movie],
        },
        {
            "relation": Directed,
            "from_collections": [Director],
            "to_collections": [Movie],
        },
    ]

    def init_graph(self):
        """
        Initializes the graph by reading data from a JSON file and creating nodes and edges.

        Returns:
            None
        """
        with open(self.corpus_file_or_dir, "r") as file:
            data = json.load(file)
        for entry in data:
            movie_node = self.upsert_node(
                "Movie",
                {
                    "title": entry["title"],
                    "year": entry["year"],
                    "genre": entry["genre"],
                    "description": entry["description"],
                },
            )
            for actor in entry["actors"]:
                actor_node = self.upsert_node(
                    "Actor", {"name": actor["name"], "birthdate": actor["birthdate"]}
                )
                self.upsert_edge(
                    "PlayedIn",
                    actor_node,
                    movie_node,
                    edge_attrs={"rating": actor["rating"]},
                )
            for director in entry["directors"]:
                director_node = self.upsert_node(
                    "Director",
                    {"name": director["name"], "birthdate": director["birthdate"]},
                )
                self.upsert_edge("Directed", director_node, movie_node)

    def create_view(self):
        """
        Creates a view for the movies collection with fuzzy search and tokenization analyzers.

        Returns:
            None
        """
        analyzer_ngram = ArangoAnalyzer("fuzzy_search_bigram")
        analyzer_ngram.set_edge_ngrams(max=3)
        analyzer_ngram.type = ArangoAnalyzer._TYPE_NGRAM
        analyzer_ngram.set_features()

        analyzer_ngram.create(self.arango_db)

        analyzer_token = ArangoAnalyzer("en_tokenizer")
        analyzer_token.set_stopwords(include_default=False)
        analyzer_token.stemming = True
        analyzer_token.accent = False
        analyzer_token.type = ArangoAnalyzer._TYPE_TEXT
        analyzer_token.set_features()

        analyzer_token.create(self.arango_db)

        link = Link(name="Movie")  # Name of a collection in the database
        link_analyzers = AnalyzerList(["fuzzy_search_bigram", "en_tokenizer"])
        link.analyzers = link_analyzers

        title_field = ViewField(
            "title", AnalyzerList(["fuzzy_search_bigram", "en_tokenizer"])
        )
        description_field = ViewField(
            "description", AnalyzerList(["fuzzy_search_bigram", "en_tokenizer"])
        )

        title_emb_field = ViewField("title_emb")
        description_emb_field = ViewField("description_emb")
        id_field = ViewField("_id")

        link.add_field(title_field)
        link.add_field(title_emb_field)

        link.add_field(description_field)
        link.add_field(description_emb_field)

        link.add_field(id_field)
        view = View("movies_view", view_type="arangosearch")
        view.add_link(link)
        view.add_primary_sort("name", asc=False)
        view.add_stored_value(["name"], compression="lz4")
        try:
            view.create(self.arango_db)
        except Exception as e:
            print("Error creating view, please delete the one on DB?", e)
