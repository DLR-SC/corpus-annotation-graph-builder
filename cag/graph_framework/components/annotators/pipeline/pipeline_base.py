import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

import tomli

from cag import logger
from cag.utils import utils
import spacy

from cag.utils.config import Config



config_path = os.path.join(  "configs", "annotator.toml")

class Pipeline(ABC):
    ANNOTATORS_CONFIG: ClassVar = tomli.loads(
        Path(config_path).read_text(encoding="utf-8"))  # default call annotators.get_annotators_config


    def __init__(self, type, database_config:Config, pipeline:dict = {}, ):
        self.type = type
        self.annotator_instances = {}
        self.pipeline= {}
        for name, is_save in pipeline.items():
            self.add_annotation_pipe(name, is_save)
        self.annotated_artifacts = None
        self.database_config = database_config

    def add_annotation_pipe(self, name, save: bool = False):
        """

        """
        cls, _ = utils.get_cls_from_path(Pipeline.ANNOTATORS_CONFIG["annotator"][name]["annotator_class"])
        instance = cls(Pipeline.ANNOTATORS_CONFIG, self.database_config)
        self.annotator_instances[name] = instance

        pipe_name = Pipeline.ANNOTATORS_CONFIG["annotator"][name]["pipe"]
        self.add_pipe(pipe_name)
        self.pipeline[name] = save

    def save(self):
        if self.annotated_artifacts is None:
            logger.error("call annotate before saving")
            pass
        for pipe, save in self.pipeline.items():
            if save:
                logger.info("saving annotations of {}".format(pipe))
                self.annotator_instances[pipe].save_annotations(self.annotated_artifacts)

    @abstractmethod
    def add_pipe(self, pipe_name, **kargs):
        pass

    @abstractmethod
    def annotate(self, texts):
        pass

    @staticmethod
    def extend_annotators(extended_config_dict_or_path: "dict|str"=None):
        config = tomli.loads(Path(config_path).read_text(encoding="utf-8"))
        if type(extended_config_dict_or_path) == str:
            extended_dic = tomli.loads(
                Path(extended_config_dict_or_path).read_text(encoding="utf-8"))
        else: extended_dic = extended_config_dict_or_path
        if extended_dic is not None:
            config.update(extended_dic)
        Pipeline.ANNOTATORS_CONFIG = config
        return config