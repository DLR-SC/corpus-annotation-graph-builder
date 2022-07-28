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
        # fetch your data, load it, etc,
        # self.corpus_file_or_dir can be used to tell your creator where to start
        # ...
        for anyset in [{'data': "Test entry #1", 'data': "Test entry #2"}]:
            any_doc = {
                'name': anyset['data']
            }
            any_doc['_key'] = utils.encode_name(any_doc['name'])
            any_vert = self.update_vert(
                AnyGraphCreator._ANY_DATASET_NODE_NAME, any_vert)
            self.upsert_link(
                AnyGraphCreator._ANY_EDGE_PUB_CORPUS, any_vert, corpus)
            # now add more ressource to this dataset

            # ...
            # you can also use self.database and self.graph to access the pyArango objects directly
