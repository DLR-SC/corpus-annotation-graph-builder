from abc import ABC, abstractmethod
from typing import ClassVar

from pyArango.document import Document
from pyArango.graph import EdgeDefinition
from pyArango.theExceptions import CreationError

from cag import logger
from cag.graph_framework.components.component import Component
from cag.utils import utils
from cag.utils.config import Config


class Annotator(ABC, Component):
    ANNOTATION_TYPE : ClassVar = ["text", "url", "image"]
    ANNOTATION_LEVEL: ClassVar = ["node", "corpus"]

    def __init__(self, annotators_config, conf: Config = None):
        super().__init__(conf)
        self.name = self.__class__.__name__
        self.annotators_config = annotators_config
        self.vertex_class_path = annotators_config["annotator"][self.name]["vertex_class"]
        self.edge_class_path = annotators_config["annotator"][self.name]["edge_class"]
        self.annotation_level = annotators_config["annotator"][self.name]["level"]
        self.annotation_type = annotators_config["annotator"][self.name]["type"]
        self.annotated_vertex = annotators_config["annotator"][self.name][ "annotated_vertex_name"]
        self.pipe_code = annotators_config["annotator"][self.name]["pipe"]

        self.vertex_name = self.vertex_class_path.split(".")[-1]
        self.edge_name = self.edge_class_path.split(".")[-1]

        self.load_pipe_component()
        self.init_graph_elts()
        is_valid, errors = self.validate()
        logger.info(f"annotator is validated: {is_valid}")
        logger.debug(f"annotator is validated: {errors}")


    def init_graph_elts(self):
        self.vertex_class, annotation_vertex = utils.get_cls_from_path(self.vertex_class_path)
        self.edge_class, relation = utils.get_cls_from_path(self.edge_class_path)

        utils.load_module(".".join(self.vertex_class_path.split(".")[:-1]))
        utils.load_module(".".join(self.edge_class_path.split(".")[:-1]))

        logger.info(f"saving relation {relation} to {annotation_vertex} and from {self.annotated_vertex}")
        #EdgeDefinition('GenericEdge', fromCollections=['GenericNode'], toCollections=['GenericNode'])
        self.graph.update_graph_structure(relation,
                                          [self.annotated_vertex],
                                          [annotation_vertex],
                                          create_collections=True
                                          )



    def load_pipe_component(self):
        module = None
        if "pipe_path" in self.annotators_config["annotator"][self.name].keys():
            self.pipe_path = self.annotators_config["annotator"][self.name]["pipe_path"]
            if self.pipe_path is not None and len(self.pipe_path) > 0:
                logger.debug("loading {}".format(self.pipe_path))
                module = utils.load_module(self.pipe_path)
        return module

    def get_pipe_func(self):
        module = self.load_pipe_component()
        pipe_func = None
        if module is not None:
            if "pipe" in self.annotators_config["annotator"][self.name].keys():
                pipe_code = self.annotators_config["annotator"][self.name]["pipe"]
                pipe_func = getattr(module, pipe_code)
        return pipe_func


    def validate(self):
        error_dict = {}
        if self.annotation_type not in Annotator.ANNOTATION_TYPE:
            error_dict["annotation_type"] = "The annotation type should have one of the following values: {} but has the value {}".\
                format(str(Annotator.ANNOTATION_TYPE), self.annotation_type)
            logger.error(error_dict["annotation_type"])

        if self.annotation_level not in Annotator.ANNOTATION_LEVEL:
            error_dict["annotation_level"] = "The annotation level should have one of the following values: {} " \
                                         "but has the value {}".\
                                          format(str(Annotator.ANNOTATION_LEVEL), self.annotation_level)
            logger.error(error_dict["annotation_level"])

        if not self.database.hasCollection(self.annotated_vertex):
            error_dict["annotated_vertex"] = "We couldnt find the *annotated_vertex* {}.".format(self.annotated_vertex)
            logger.error(error_dict["annotated_vertex"])

        if not self.database.hasCollection(self.vertex_name):
            error_dict["vertex_class"] = "The vertex was not created, *vertex_class_path*: {}.".format(self.vertex_class_path)
            logger.error(error_dict["vertex_class"])

        if not self.database.hasCollection(self.edge_name):
            error_dict["edge_class"] = "The edge was not created, *edge_class_path*: {}.".format(self.edge_class_path)
            logger.error(error_dict["edge_class"])

        is_valid = not bool(error_dict)
        return is_valid, error_dict


    @abstractmethod
    def create_vertex(self, **kwargs) -> Document:
        pass

    @abstractmethod
    def create_edge(self, _from: Document, _to: Document, **kwargs) -> Document:
        pass

    @abstractmethod
    def save_annotations(self, annotated_text: "[]"):
        pass


