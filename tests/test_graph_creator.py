import pytest
import requests

from cag.framework import GraphCreatorBase
from cag.graph_elements.nodes import GenericOOSNode, Field
from cag.graph_elements.relations import GenericEdge
from cag.utils.config import Config
from tests import config_factory


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
    _description = "Graph based on the DLR elib corpus"

    _edge_definitions = [
        {
            "relation": "HasRelation",
            "from_collections": [CollectionA._name],
            "to_collections": [CollectionB._name],
        },
        {
            "relation": "HasAnotherRelation",
            "from_collections": [CollectionC._name],
            "to_collections": [CollectionC._name],
        },
    ]

    def init_graph(self):
        pass


class TestGC:
    def test_arango_connection_success(self):
        """
        Unit test for verifying the connection to an ArangoDB instance.

        This function tests that the ArangoDB instance specified in the configuration can be connected to and that the
        database name specified in the configuration matches the name of the instance being used for testing.


        Raises:
            AssertionError: If the configuration is incorrect or the connection to the database fails.
        """
        config = config_factory()
        assert config.arango_db.name == config.database

    def test_arango_connection_fail(self):
        """
        Test the behavior of the `Config` class when trying to connect to an ArangoDB instance with a wrong host.
        Raises:
            AssertionError: if the ConnectionError is not raised

        """

        with pytest.raises(requests.exceptions.ConnectionError):
            Config(
                url=f"http://wrong_host",
                user="root",
                password="",
                graph="SampleGraph",
                database="database",
            )

    def test_create_collection(self):
        """
        Unit test for creating collections in an ArangoDB database.

        This function tests the creation of three collections in the ArangoDB database specified in the
        configuration: "CollectionA", "CollectionB", and "HasRelation". It asserts that each of the collections
        was created successfully by checking if the `arango_db` object
        in the configuration has a collection with the corresponding name.

        Returns:
            None.

        Raises:
            AssertionError: If any of the collections were not created successfully or do not exist.
        """

        config = config_factory()
        SampleGraphCreator("", config_factory())
        assert config.arango_db.has_collection("CollectionA")
        assert config.arango_db.has_collection("CollectionB")
        assert config.arango_db.has_collection("HasRelation")

    def test_node_creation(self):
        """
        Unit test for creating and upserting nodes and edges in an ArangoDB graph.

        This function tests the creation of nodes and edges in an ArangoDB graph using the `SampleGraphCreator` class.
        It first creates a `SampleGraphCreator` and the configuration returned by `config_factory()`.
        Then it creates two nodes, one in "CollectionA" with the key "v1" and a value of "val1",
        and another in "CollectionB" with the key "v2" and a value of "val2". It asserts that the nodes were created
        successfully by checking if they exist in their respective collections using their keys.
        Finally, it creates an edge between the two nodes in the "HasRelation" collection,
        and asserts that the edge was created successfully by checking if it exists in the collection using the keys of the nodes.

        Returns:
            None.

        Raises:
            AssertionError: If any of the nodes or edges were not created successfully or do not exist.
        """

        config = config_factory()
        gc = SampleGraphCreator("", config)

        node1 = gc.upsert_node(
            CollectionA._name, {"value": "val1", "_key": "v1"}
        )
        assert (
            config.arango_db.collection("CollectionA").get("v1")
            == node1.getStore()
        )

        node2 = gc.upsert_node(
            CollectionB._name, {"value": "val2", "_key": "v2"}
        )
        assert (
            config.arango_db.collection("CollectionB").get("v2")
            == node2.getStore()
        )

        edge = gc.upsert_edge("HasRelation", node1, node2)
        assert (
            config.arango_db.collection("HasRelation").get(
                "CollectionA-v1-CollectionB-v2"
            )
            == edge.getStore()
        )

    def test_node_upsert(self):
        """
        Unit test for upserting nodes in an ArangoDB graph.

        This function tests the updating of nodes in an ArangoDB graph using the `SampleGraphCreator` class.
        Then it creates a node in the "CollectionA" collection with the key "v1" and a value of "val1" and
        a second value of "no change". It upserts the same node again with a new value of "val2" and asserts that the
         node was updated successfully by comparing the revision and timestamp fields of the original and updated nodes.
          It also checks that the "value2" field of the node was not changed during the update.

        Returns:
            None.

        Raises:
            AssertionError: If the node was not updated successfully or its fields were changed unexpectedly.
        """

        config = config_factory()
        gc = SampleGraphCreator("", config)
        node = gc.upsert_node(
            CollectionA._name,
            {"value": "val1", "value2": "no change", "_key": "v1"},
        )
        node2 = gc.upsert_node(
            CollectionA._name, {"value": "val2", "_key": "v1"}
        )
        assert node["_rev"] != node2["_rev"]
        assert node["timestamp"] != node2["timestamp"]
        assert node2["value"] == "val2"
        assert node2["value2"] == "no change"

    def test_edge_cases(self):
        """
        Unit test for edge cases in creating nodes and edges in an ArangoDB graph.

        This function tests edge cases in creating nodes and edges in an ArangoDB graph using the `SampleGraphCreator` class.
        It then attempts to create a node in an unknown collection and asserts that a `KeyError` is raised.
        It creates a node in the "CollectionC" collection with the key "v1" and a value of "val1" and a second value
        of "no change", and creates an edge between this node and itself in the "HasRelation" collection.
        This tests whether self-loops can be created successfully in the graph.

        Returns:
            None.

        Raises:
            AssertionError: If the `KeyError` is not raised or the self-loop edge was not created successfully.
        """

        config = config_factory()
        gc = SampleGraphCreator("", config)
        with pytest.raises(KeyError):
            gc.upsert_node(
                "UnknownCollection",
                {"value": "val1", "value2": "no change", "_key": "v1"},
            )
        node = gc.upsert_node(
            CollectionC._name,
            {"value": "val1", "value2": "no change", "_key": "v1"},
        )
        edge = gc.upsert_edge("HasRelation", node, node)

    def test_node_removal(self):
        """
        Unit test for removing nodes from an ArangoDB graph.

        This function tests removing nodes from an ArangoDB graph using the `SampleGraphCreator` class.

        It then creates a node in the "CollectionA" collection with the key "v1" and a value of "val1".
        It asserts that the node is present in the collection using its key. It then deletes the node and asserts that
        it is no longer present in the collection.

        Returns:
            None.

        Raises:
            AssertionError: If the node is not deleted successfully.
        """

        config = config_factory()
        gc = SampleGraphCreator("", config)

        node1 = gc.upsert_node(
            CollectionA._name, {"value": "val1", "_key": "v1"}
        )
        assert (
            config.arango_db.collection("CollectionA").get("v1")
            == node1.getStore()
        )
        node1.delete()
        assert config.arango_db.collection("CollectionA").get("v1") is None

    def test_upsert_edge(self):
        """
        Test the upsert_edge method of SampleGraphCreator.

        This method creates two nodes in CollectionA and CollectionB using the upsert_node method of SampleGraphCreator,
         and then creates an edge between them using the upsert_edge method. It asserts that the nodes and edge were
         created and stored correctly in the ArangoDB database specified in the config object.


        """
        config = config_factory()
        gc = SampleGraphCreator("", config)

        node1 = gc.upsert_node(
            CollectionA._name, {"value": "val1", "_key": "v1"}
        )
        assert (
            config.arango_db.collection("CollectionA").get("v1")
            == node1.getStore()
        )

        node2 = gc.upsert_node(
            CollectionB._name, {"value": "val2", "_key": "v2"}
        )
        assert (
            config.arango_db.collection("CollectionB").get("v2")
            == node2.getStore()
        )

        edge = gc.upsert_edge("HasRelation", node1, node2)
        assert (
            config.arango_db.collection("HasRelation").get(
                "CollectionA-v1-CollectionB-v2"
            )
            == edge.getStore()
        )
        edge = gc.upsert_edge("HasRelation", node1, node1)
        assert (
            config.arango_db.collection("HasRelation").get(
                "CollectionA-v1-CollectionA-v1"
            )
            == edge.getStore()
        )

    def test_relation_removal(self):
        """
        Test if a relation can be removed correctly.

        Creates two nodes and an edge between them, upserts them into the database using the SampleGraphCreator class
        and then removes the edge between them. Checks if the edge has been successfully removed.

        """
        config = config_factory()
        gc = SampleGraphCreator("", config)

        node1 = gc.upsert_node(
            CollectionA._name, {"value": "val1", "_key": "v1"}
        )
        assert (
            config.arango_db.collection("CollectionA").get("v1")
            == node1.getStore()
        )

        node2 = gc.upsert_node(
            CollectionB._name, {"value": "val2", "_key": "v2"}
        )
        assert (
            config.arango_db.collection("CollectionB").get("v2")
            == node2.getStore()
        )

        edge = gc.upsert_edge("HasRelation", node1, node2)
        assert (
            config.arango_db.collection("HasRelation").get(
                "CollectionA-v1-CollectionB-v2"
            )
            == edge.getStore()
        )
        edge.delete()
        assert (
            config.arango_db.collection("HasRelation").get(
                "CollectionA-v1-CollectionB-v2"
            )
            is None
        )
