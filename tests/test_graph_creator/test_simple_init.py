import pytest

from cag.framework import GraphCreatorBase
from cag.graph_elements.nodes import GenericOOSNode, Field
from cag.graph_elements.relations import GenericEdge
from . import config


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


class SampleGraphCreator(GraphCreatorBase):
    _name = "SampleGraphCreator"
    _description = "Graph based on the DLR elib corpus"

    _edge_definitions = [
        {
            'relation': "HasRelation",
            'from_collections': [CollectionA._name],
            'to_collections': [CollectionB._name]
        },
        {
            'relation': "HasAnotherRelation",
            'from_collections': [CollectionC._name],
            'to_collections': [CollectionC._name]
        }
    ]

    def init_graph(self):
        pass


class TestGCBasics:
    def test_arango_connection(self):
        assert config.arango_db.name == "test"

    def test_create_collection(self):
        SampleGraphCreator("", config, initialize=False)
        assert config.arango_db.has_collection("CollectionA")
        assert config.arango_db.has_collection("CollectionB")
        assert config.arango_db.has_collection("HasRelation")

    def test_node_creation(self):
        gc = SampleGraphCreator("", config, initialize=False)

        node1 = gc.upsert_node(CollectionA._name, {"value": "val1", "_key": "v1"})
        assert config.arango_db.collection("CollectionA").get("v1") == node1.getStore()

        node2 = gc.upsert_node(CollectionB._name, {"value": "val2", "_key": "v2"})
        assert config.arango_db.collection("CollectionB").get("v2") == node2.getStore()

        edge = gc.upsert_edge("HasRelation", node1, node2)
        assert config.arango_db.collection("HasRelation").get("CollectionA-v1-CollectionB-v2") == edge.getStore()

    def test_node_upsert(self):
        gc = SampleGraphCreator("", config, initialize=False)
        node = gc.upsert_node(CollectionA._name, {"value": "val1", "value2": "no change", "_key": "v1"})
        node2 = gc.upsert_node(CollectionA._name, {"value": "val2", "_key": "v1"})
        assert node["_rev"] != node2["_rev"]
        assert node["timestamp"] != node2["timestamp"]
        assert node2["value"] == "val2"
        assert node2["value2"] == "no change"

    def test_edge_cases(self):
        gc = SampleGraphCreator("", config, initialize=False)
        with pytest.raises(KeyError):
            gc.upsert_node("UnknownCollection", {"value": "val1", "value2": "no change", "_key": "v1"})
        node = gc.upsert_node(CollectionC._name, {"value": "val1", "value2": "no change", "_key": "v1"})
        # this shouldn't work
        edge = gc.upsert_edge("HasRelation", node, node)
