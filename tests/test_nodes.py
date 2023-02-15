from cag.graph_elements.base_graph import BaseGraph

from pyArango.graph import Graph, EdgeDefinition

import cag.utils as utils
from cag.framework import GraphCreatorBase
import datetime
import inspect


class SampleGraph(BaseGraph):
    _edgeDefinitions = [
        EdgeDefinition(
            "GenericEdge",
            fromCollections=["GenericNode"],
            toCollections=["GenericNode"],
        )
    ]
    _orphanedCollections = []


def whoami():
    frame = inspect.getouterframes(inspect.currentframe())[1]
    return frame.function


class AnyGraphCreator(GraphCreatorBase):
    _ANY_DATASET_NODE_NAME = "AnyDataset"
    _ANY_EDGE_PUB_CORPUS = "AnyEdgeDSCorpus"
    _name = "Any Graph Creator"
    _description = "Creates a graph based on any corpus"
    _edge_definitions = [
        {
            "relation": _ANY_EDGE_PUB_CORPUS,
            "from_collections": [_ANY_DATASET_NODE_NAME],
            "to_collections": [GraphCreatorBase._CORPUS_NODE_NAME],
        }
    ]

    def __init__(self, corpus_dir, config, initialize=False):
        super().__init__(corpus_dir, config, initialize)

    def init_graph(self):
        corpus = self.create_corpus_node(
            key="AnyCorpus",
            name=AnyGraphCreator._name,
            type="journal",
            desc=AnyGraphCreator._description,
            created_on=datetime.datetime.today(),
        )
