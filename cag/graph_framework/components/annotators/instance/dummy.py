from pyArango.document import Document
from cag import logger
from cag.graph_framework.components.annotators.element.annotator import Annotator


class DummyDefaultAnnotator(Annotator):

    def create_edge(self, _from: Document, _to: Document, **kwargs) -> Document:
        pass


    def create_vertex(self, **kwargs) -> Document:
        pass

    def save_annotations(self, annotated_text: "[]"):
        pass


def customized_pipe_func(input):
    logger.debug("checking Dummy customized pipe")
    return input