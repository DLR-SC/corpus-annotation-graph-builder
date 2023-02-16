from cag.utils.config import configuration

from ..test_nodes import *
from ..text_db_fixture import *


class TestGCBasics:
    def test_arango_connection(self):
        config = configuration(database=whoami())
        assert config.arango_db.name == whoami()

    def test_gc_creation(self):
        config = configuration(graph="SampleGraph", database=whoami())
        gc = AnyGraphCreator("", config)
        assert config.arango_db.has_collection(
            AnyGraphCreator._ANY_DATASET_NODE_NAME
        )
        assert config.arango_db.has_collection(
            AnyGraphCreator._ANY_EDGE_PUB_CORPUS
        )
        assert not config.arango_db[AnyGraphCreator._CORPUS_NODE_NAME].has(
            "AnyCorpus"
        )

    def test_gc_creation(self):
        config = configuration(graph="SampleGraph", database=whoami())
        gc = AnyGraphCreator("", config, initialize=True)
        assert config.arango_db[AnyGraphCreator._CORPUS_NODE_NAME].has(
            "AnyCorpus"
        )
