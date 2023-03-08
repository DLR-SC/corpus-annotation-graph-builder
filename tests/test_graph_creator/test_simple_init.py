import os

import pytest

from cag.framework import GraphCreatorBase
from cag.graph_elements.nodes import GenericOOSNode, Field
from cag.graph_elements.relations import GenericEdge
from cag.utils.config import Config
from tests.test_graph_creator import config_factory


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


class TestGCBasics:
    def test_arango_connection(self):
        config = config_factory()
        assert config.arango_db.name == config.database

    def test_create_collection(self):
        config = config_factory()
        SampleGraphCreator("", config_factory())
        assert config.arango_db.has_collection("CollectionA")
        assert config.arango_db.has_collection("CollectionB")
        assert config.arango_db.has_collection("HasRelation")

    def test_node_creation(self):
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
