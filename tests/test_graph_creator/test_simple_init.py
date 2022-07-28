from cag.utils.config import configuration
import cag.utils as utils
from cag.graph_framework.components import GraphCreatorBase
import datetime


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

    def __init__(self, corpus_dir, database, initialize=False):
        super().__init__(corpus_dir, database, initialize)

    def init_graph(self):
        corpus = self.create_corpus_vertex(key="AnyCorpus",
                                           name=AnyGraphCreator._name,
                                           type="journal",
                                           desc=AnyGraphCreator._description,
                                           created_on=datetime.today())
def test_arango_creation():
    config=configuration()