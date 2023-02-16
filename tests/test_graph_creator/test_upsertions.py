from ..test_nodes import *
from cag.utils.config import configuration
from ..text_db_fixture import *


class TestGCUpserts:
    def test_upsert(self):
        config = configuration(graph="SampleGraph", database=whoami())
        config_2 = configuration(graph="SampleGraph", database=whoami())
        gc = AnyGraphCreator("", config)
        gc.upsert_node(
            AnyGraphCreator._ANY_DATASET_NODE_NAME,
            {"_key": "test_1", "name": "before_upsert"},
        )
        vert = config.arango_db[AnyGraphCreator._ANY_DATASET_NODE_NAME][
            "test_1"
        ]
        assert vert is not None
        assert vert["name"] == "before_upsert"

        gc.upsert_node(
            AnyGraphCreator._ANY_DATASET_NODE_NAME,
            {"_key": "test_1", "name": "after_upsert"},
        )
        # other connection, should still be updated
        vert = config_2.arango_db[AnyGraphCreator._ANY_DATASET_NODE_NAME][
            "test_1"
        ]
        assert vert is not None
        assert vert["name"] == "after_upsert"

        # only update the correct doc
        gc.upsert_node(
            AnyGraphCreator._ANY_DATASET_NODE_NAME,
            {"_key": "test_1", "name": "before_insert"},
        )
        vert = config.arango_db[AnyGraphCreator._ANY_DATASET_NODE_NAME][
            "test_1"
        ]
        assert vert is not None
        assert vert["name"] == "before_insert"

        gc.upsert_node(
            AnyGraphCreator._ANY_DATASET_NODE_NAME,
            {"_key": "test_2", "name": "after_insert"},
        )
        # other connection, should still be updated
        vert = config_2.arango_db[AnyGraphCreator._ANY_DATASET_NODE_NAME][
            "test_1"
        ]
        assert vert is not None
        assert vert["name"] == "before_insert"
        vert = config_2.arango_db[AnyGraphCreator._ANY_DATASET_NODE_NAME][
            "test_2"
        ]
        assert vert is not None
        assert vert["name"] == "after_insert"

    def test_upsert_alt_key(self):
        config = configuration(graph="SampleGraph", database=whoami())
        config_2 = configuration(graph="SampleGraph", database=whoami())
        gc = AnyGraphCreator("", config)
        gc.upsert_node(
            AnyGraphCreator._ANY_DATASET_NODE_NAME,
            {"_key": "test_1", "key_alt": "test_alt", "name": "before_upsert"},
        )
        vert = config.arango_db[AnyGraphCreator._ANY_DATASET_NODE_NAME][
            "test_1"
        ]
        assert vert is not None
        assert vert["name"] == "before_upsert"
        gc.upsert_node(
            AnyGraphCreator._ANY_DATASET_NODE_NAME,
            {"key_alt": "test_alt", "name": "after_upsert"},
            alt_key="key_alt",
        )
        # other connection, should still be updated (on the alt key)
        vert = config_2.arango_db[AnyGraphCreator._ANY_DATASET_NODE_NAME][
            "test_1"
        ]
        assert vert is not None
        assert vert["name"] == "after_upsert"
