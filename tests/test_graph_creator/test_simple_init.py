from cag.utils.config import configuration
import cag.utils as utils
from cag.graph_framework.components import GraphCreatorBase
import datetime
from .test_nodes import *
import inspect


class AnyGraphCreator(GraphCreatorBase):
    _ANY_DATASET_NODE_NAME = "AnyDataset"
    _ANY_EDGE_PUB_CORPUS = "AnyEdgeDSCorpus"
    _name = "Any Graph Creator"
    _description = "Creates a graph based on any corpus"
    _edge_definitions = [
        {
            'relation': _ANY_EDGE_PUB_CORPUS,
            'from_collections': [_ANY_DATASET_NODE_NAME],
            'to_collections': [GraphCreatorBase._CORPUS_NODE_NAME]
        }
    ]

    def __init__(self, corpus_dir, config, initialize=False):
        super().__init__(corpus_dir, config, initialize)

    def init_graph(self):
        corpus = self.create_corpus_vertex(key="AnyCorpus",
                                           name=AnyGraphCreator._name,
                                           type="journal",
                                           desc=AnyGraphCreator._description,
                                           created_on=datetime.today())


def whoami():
    frame = inspect.currentframe()
    return inspect.getframeinfo(frame).function


class TestGCBasics:
    def test_arango_connection(self):
        config = configuration(database=whoami())
        assert config.arango_db.name == whoami()

    def test_gc_creation(self):
        config = configuration(graph='SampleGraph', database=whoami())
        gc = AnyGraphCreator("", config)
        assert config.arango_db.has_collection(
            AnyGraphCreator._ANY_DATASET_NODE_NAME)
