from cag.graph_framework.components import AnnotatorBase
from cag.utils.config import *

from graph_creation_example import AnyGraphCreator
from pyArango.query import AQLQuery


class AnyAnnotator(AnnotatorBase):
    def __init__(self, conf: Config, params={'mode': 'run-1'}, filter_annotatable=True):
        super().__init__(query=f"""FOR dp IN {AnyGraphCreator._ANY_DATASET_NODE_NAME}
        RETURN dp
        """, params=params, conf=conf, filter_annotatable=filter_annotatable, run=True)

    def update_graph(self, timestamp, data: AQLQuery):
        for dp in data:
            pass
