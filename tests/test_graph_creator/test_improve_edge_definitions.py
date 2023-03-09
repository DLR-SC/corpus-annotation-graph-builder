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


class SampleGraphCreator(GraphCreatorBase):
    _name = "SampleGraphCreator"
    _description = "Graph based on the DLR elib corpus"

    _edge_definitions = [
        {
            "relation": HasRelation,
            "from_collections": [CollectionA],
            "to_collections": [CollectionB],
        },
        {
            "relation": HasAnotherRelation,
            "from_collections": [CollectionC],
            "to_collections": [CollectionC],
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
        SampleGraphCreator("", config_factory())
        assert config.arango_db.has_collection("CollectionA")
        assert config.arango_db.has_collection("CollectionB")
        assert config.arango_db.has_collection("HasRelation")