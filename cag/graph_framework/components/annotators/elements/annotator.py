from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from pathlib import Path
from typing import List, ClassVar

import tomli

from cag import logger
from cag.graph_framework.components.component import Component
from cag.utils import utils
from cag.utils.config import Config


class Annotator(ABC, Component):

    def __init__(self, annotators_config, conf: Config = None):
        super().__init__(conf)
        name = self.__class__.__name__
        self.annotators_config = annotators_config
        self.vertex_class_path = annotators_config["annotator"][name]["vertex_class"]
        self.edge_class_path = annotators_config["annotator"][name]["edge_class"]
        self.annotation_level = annotators_config["annotator"][name]["level"]
        self.annotated_vertex = annotators_config["annotator"][name][
            "annotated_vertex_name"]  # the name of the vertex where the annotation will be linked from

        # NAME:ClassVar = "ner" # this name should match the name in the annotator.TOML file
        self.vertex_name = self.vertex_class_path.split(".")[-1]
        self.edge_name = self.edge_class_path.split(".")[-1]
        self.init_graph_elts()
        ## settings

    def init_graph_elts(self):
        self.vertex_class, _ = utils.get_cls_from_path(self.vertex_class_path)
        self.edge_class, _ = utils.get_cls_from_path(self.edge_class_path)

        if not self.database.hasCollection(self.vertex_name):
            logger.info('creating collection name', self.vertex_name)
            self.database.createCollection(self.vertex_name)

        if not self.database.hasCollection(self.edge_name):
            logger.info('creating edge name', self.edge_name)
            self.database.createCollection(self.edge_name)

    @abstractmethod
    def create_vertex(self, **kargs):
        pass

    @abstractmethod
    def save_annotations(self, annotated_text: "[]"):
        pass
