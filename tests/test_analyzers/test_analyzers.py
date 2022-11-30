from cag.framework import AnalyzerBase
from cag.graph_elements.base_graph import BaseGraph

from pyArango.graph import EdgeDefinition

import cag.utils as utils
from cag.utils.config import *

from ..test_nodes import *
import networkx as nx


class AnylzerGC(GraphCreatorBase):
    _ANY_DATASET_NODE_NAME = "AnyDataset"
    _ANY_EDGE_PUB_CORPUS = "AnyEdgeDSCorpus"
    _name = "Any Graph Creator"
    _description = "Creates a graph based on any corpus"
    _edge_definitions = [
        {
            'relation': _ANY_EDGE_PUB_CORPUS,
            'from_collections': [_ANY_DATASET_NODE_NAME],
            'to_collections': [GraphCreatorBase._CORPUS_NODE_NAME, _ANY_DATASET_NODE_NAME]
        }
    ]

    def __init__(self, corpus_dir, config, initialize=True):
        super().__init__(corpus_dir, config, initialize)

    def init_graph(self):
        corpus = self.create_corpus_node(key="analyzer_corpus",
                                           name=AnyGraphCreator._name,
                                           type="journal",
                                           desc=AnyGraphCreator._description,
                                           created_on=datetime.datetime.today())
        prev_vert = corpus
        for i in range(10):
            doc = {
                '_key': f"test_{i}",
                'text': f"TEST TEXT {i}"
            }
            vert = self.upsert_node(AnylzerGC._ANY_DATASET_NODE_NAME, doc)
            self.upsert_edge(AnylzerGC._ANY_EDGE_PUB_CORPUS, prev_vert, vert)
            prev_vert = vert


class AnyAnalyzer(AnalyzerBase):
    def __init__(self, conf: Config):
        super().__init__(config=conf, run=True, query="""
         FOR path IN 1..10 ANY K_PATHS 'Corpus/analyzer_corpus' TO 'AnyDataset/test_9' AnyEdgeDSCorpus
                RETURN path
        """)

    def run(self, data):
        data = list(data)
        self.networkx = self.create_networkx(data, weight_edges=True)


class TestAnnotatorBasics:
    def test_create_nx(self):
        
        conf = configuration(graph='SampleGraph', database=whoami())
        gc = AnylzerGC("", config=conf)
        # act
        an = AnyAnalyzer(conf)
        g = an.networkx
        # assert that nx build correctly
        avg_l = nx.average_shortest_path_length(g)
        assert avg_l==4.0
