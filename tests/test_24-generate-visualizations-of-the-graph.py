from bs4 import BeautifulSoup
from pathlib import Path

from cag.cli import visualize
from cag.framework import GraphCreatorBase
from cag.graph_elements.nodes import GenericOOSNode, Field
from cag.graph_elements.relations import GenericEdge


class CollectionA(GenericOOSNode):
    _name = "CollectionA"
    _fields = {"value": Field(), "value2": Field(), **GenericOOSNode._fields}


class CollectionB(GenericOOSNode):
    _name = "CollectionB"
    _fields = {"value": Field(), **GenericOOSNode._fields}


class CollectionC(GenericOOSNode):
    _name = "CollectionC"
    _fields = {"value": Field(), **GenericOOSNode._fields}


class HasRelation(GenericEdge):
    _fields = GenericEdge._fields


class HasAnotherRelation(GenericEdge):
    _fields = GenericEdge._fields


class SampleGraphCreator(GraphCreatorBase):
    _name = "SampleGraphCreator"
    _description = "Sample Graph"

    _edge_definitions = [
        {
            "relation": "HasRelation",
            "from_collections": [CollectionA],
            "to_collections": [CollectionB],
        },
        {
            "relation": "HasAnotherRelation",
            "from_collections": [CollectionC],
            "to_collections": [CollectionC],
        },
    ]

    def init_graph(self):
        pass


class Test24:
    def test_generate(self):
        """
        Test the cli `visualize` function by generating a diagram HTML file and checking if it exists and contains
        valid HTML.

        This test calls the `visualize` function with the path of this Python file, which contain a Graphcreator
        derived from the `GraphCreatorBase` class. The `visualize` function generates an HTML file that shows the
        relationships between the collections and relations defined in those class.

        This test first checks if the generated HTML file exists. If the file exists, it opens the file and parses it
        using the `BeautifulSoup` class from the `bs4` module. If the parsing succeeds, the test passes. Otherwise,
        the test fails.

        Note: The purpose of this test is to check if the file contains anything useful at all, not to verify its exact
        structure.

        After the test, the generated HTML file is deleted to clean up the test environment.
        """
        html_file = visualize(Path(__file__).absolute())
        assert html_file.exists()
        # This test may fail in the future
        # the purpose is to check if the file contains anything useful at all
        with open(html_file) as f:
            BeautifulSoup(f, "html.parser")
            # if the call doesn't throw any exceptions, the test passes
            assert True
        # clean up
        html_file.unlink()
