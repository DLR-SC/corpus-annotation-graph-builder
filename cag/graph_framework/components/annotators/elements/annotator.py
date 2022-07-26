from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from typing import List, ClassVar

from cag.utils import utils
from cag.utils.config import Config, configuration


@dataclass
class Annotator(ABC):
    name:str
    vertex_class_path:str
    edge_class_path:str
    config: Config
    annotation_level:str = "text" #LEVEL_TEXT

    ## Constants - the annotation can be on the level of 1 node, text or on a corpus level
    LEVEL_TEXT: ClassVar = "text"
    LEVEL_CORPUS: ClassVar = "corpus"

## if conf is None:
    #     conf = configuration(use_global_conf=True)
    #  self.conf = conf
    #  self.database = conf.db
    #   self.graph_name = conf.graph



    def __post_init__(self):
        if self.config is None:
            self.config = configuration(use_global_conf=True)
        database = self.config.db
        #self.conf = conf
        #self.graph_name = conf.graph

        self.vertex_class, vertex_name = utils.get_cls_from_path(self.vertex_class_path)
        self.edge_class, edge_name = utils.get_cls_from_path(self.edge_class_path)

        if not database.hasCollection(vertex_name):
            print('creating collection name', vertex_name)
            database.createCollection(vertex_name)

        if not database.hasCollection(edge_name):
            print('creating edge name', edge_name)
            database.createCollection(edge_name)

    @abstractmethod
    def create_vertex(self, **kargs):
        pass

    @abstractmethod
    def save_annotations(self, annotated_text:"[]")
        pass