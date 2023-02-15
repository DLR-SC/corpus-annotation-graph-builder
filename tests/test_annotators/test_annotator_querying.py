from cag.framework import GenericAnnotator
from cag.graph_elements.base_graph import BaseGraph

from pyArango.graph import EdgeDefinition

import cag.utils as utils
from cag.utils.config import *

from ..test_nodes import *


class AnyAnnotator(GenericAnnotator):
    def __init__(self, conf: Config, params={"mode": "run-1"}, filter_annotatable=True):
        super().__init__(
            query=f"""FOR dp IN {AnyGraphCreator._ANY_DATASET_NODE_NAME}
        RETURN dp
        """,
            params=params,
            conf=conf,
            filter_annotatable=filter_annotatable,
        )

    def update_graph(self, timestamp):
        return super().update_graph(timestamp)


class TestAnnotatorBasics:
    def test_simple_fetch(self):
        conf = configuration(graph="SampleGraph", database=whoami())
        gc = AnyGraphCreator("", config=conf)

        conf.arango_db[AnyGraphCreator._ANY_DATASET_NODE_NAME].insert_many(
            [
                {"_key": "test_1", "name": "test_name"},
                {"_key": "test_2", "name": "Hello"},
                {"_key": "test_3", "name": "World"},
                {"_key": "test_4", "name": "ArangoDB"},
            ]
        )
        annotator = AnyAnnotator(conf)

        assert len(annotator.fetch_annotator_data()) == 4

        docs = list(annotator.fetch_annotator_data())
        docs[0]["ann"] = base64.b64encode(docs[0]["name"].encode("utf-8")).decode(
            "utf-8"
        )
        annotator.complete_annotation(docs[0])

        # after completing one annotation only three docs should remain
        conf = configuration(graph="SampleGraph", database=whoami())
        annotator = AnyAnnotator(conf)
        assert len(annotator.fetch_annotator_data()) == 3

        # however, when changing the params it should have 4 again!
        conf = configuration(graph="SampleGraph", database=whoami())
        annotator = AnyAnnotator(conf, params={"mode": "run-2"})
        assert len(annotator.fetch_annotator_data()) == 4
        # or when disabling the filter: default OFF!
        conf = configuration(graph="SampleGraph", database=whoami())
        annotator = AnyAnnotator(conf, filter_annotatable=False)
        assert len(annotator.fetch_annotator_data()) == 4
