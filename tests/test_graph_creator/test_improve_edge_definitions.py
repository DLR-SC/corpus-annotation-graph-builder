# Tests for https://github.com/DLR-SC/corpus-annotation-graph-builder/issues/25

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


class HasAnotherAnotherRelation(GenericEdge):
    _fields = GenericEdge._fields


class SampleGraphCreator(GraphCreatorBase):
    _name = "SampleGraphCreator"
    _description = "Graph based on the DLR elib corpus"

    # Testing mixed definitions (Class based and string based)
    _edge_definitions = [
        {  # new style
            "relation": HasRelation,
            "from_collections": [CollectionA],
            "to_collections": [CollectionB],
        },
        {
            "relation": HasAnotherRelation,
            "from_collections": [CollectionC],
            "to_collections": [CollectionC],
        },
        {  # old style
            "relation": HasAnotherAnotherRelation,
            "from_collections": [CollectionA],
            "to_collections": [CollectionA],
        },
    ]

    def init_graph(self):
        pass


class TestGC25:
    def test_arango_connection(self):
        config = config_factory()
        assert config.arango_db.name == config.database

    def test_create_collection(self):
        config = config_factory()
        gc = SampleGraphCreator("", config_factory())
        assert config.arango_db.has_collection("CollectionA")
        assert config.arango_db.has_collection("CollectionB")
        assert config.arango_db.has_collection("CollectionC")
        assert config.arango_db.has_collection("HasRelation")
        assert config.arango_db.has_collection("HasAnotherRelation")

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
