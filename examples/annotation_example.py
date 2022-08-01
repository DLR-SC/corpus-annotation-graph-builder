from cag.graph_framework.components import AnnotatorBase
from cag.utils.config import *

from graph_creation_example import AnyGraphCreator
from pyArango.query import AQLQuery

from pyArango.collection import Collection

from cag.graph_framework.components.annotators.pipeline import Pipeline
class AnyAnnotator(AnnotatorBase):
    def __init__(self, conf: Config, params={'mode': 'run-1'}, filter_annotatable=True):
        super().__init__(query=f"""FOR dp IN {AnyGraphCreator._ANY_DATASET_NODE_NAME}
        RETURN dp
        """, params=params, conf=conf, filter_annotatable=filter_annotatable, run=True)

    def update_graph(self, timestamp, data: AQLQuery):
        for dp in data:
            pass


## Pipeline for specialized annotator
def run_sample(config):
    pipeline: Pipeline = Pipeline(database_config=config)
    # Pipeline.extend_config(extened_dict)

    pipeline.add_annotation_pipe("NamedEntityAnnotator", True)

    coll: Collection = pipeline.database_config.db["TextNode"]
    docs = coll.fetchAll(limit=500)
    processed = []
    for txt_node in docs:
        processed.append((txt_node.text, {"_key": txt_node._key}))
    pipeline.annotate(processed)

    pipeline.save()
