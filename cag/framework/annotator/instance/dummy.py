from pyArango.document import Document
from cag import logger
from cag.framework.annotator.element.orchestrator import PipeOrchestrator


class DummyPipeOrchestrator(PipeOrchestrator):
    def create_edge(self, _from: Document, _to: Document, **kwargs) -> Document:
        pass

    def create_node(self, **kwargs) -> Document:
        pass

    def save_annotations(self, annotated_text: "[]"):
        pass


def customized_pipe_func(input):
    logger.debug("checking Dummy customized pipe")
    return input
