import os
from pathlib import Path
from typing import List, ClassVar

import tomli
from pyArango.database import Database

from  cag.graph_framework.components.annotators.textmining_pipes import *
from cag import logger
from cag.utils import utils
import spacy

from cag.utils.config import Config

SPACY_LANGUAGE_PACKAGE: ClassVar = {
        # English pipeline optimized for CPU. Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer.
        # 12 MB
        "en_sm": "en_core_web_sm",

        # English pipeline optimized for CPU. Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer.
        # 31 MB
        "en_md": "en_core_web_lg",
        # English pipeline optimized for CPU. Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer.

        # English pipeline optimized for CPU. Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer.
        # 382 MB
        "en_lg": "en_core_web_lg",

        # English transformer pipeline (roberta-base). Components: transformer, tagger, parser, ner, attribute_ruler, lemmatizer.
        # 438 MB
        "en_w_transformer_roberta": "en_core_web_trf",

    }

config_path = os.path.join(  "configs", "annotator.toml")

class Pipeline:
    ANNOTATORS_CONFIG: ClassVar = tomli.loads(
        Path(config_path).read_text(encoding="utf-8"))  # default call annotators.get_annotators_config

    @staticmethod
    def extend_annotators(extended_config_dict=None):
        config = tomli.loads(Path(config_path).read_text(encoding="utf-8"))
        if extended_config_dict is not None:
            config.update(extended_config_dict)
        Pipeline.ANNOTATORS_CONFIG = config
        return config


    def __init__(self, pipeline:dict = {},
                 language_package= SPACY_LANGUAGE_PACKAGE["en_sm"],
                 database_config:Config = None):
        self.pipeline = pipeline
        self.language_package = language_package


        if not spacy.util.is_package(self.language_package):
            spacy.cli.download(self.language_package)

        self.nlp = spacy.load(self.language_package, disable=['ner'])
        self.annotator_instances = {}
        self.pipeline= {}
        for name, is_save in pipeline.items():
            self.add_annotation_pipe(name, is_save)
        self.annotated_text = None

        self.database_config = database_config

    def add_pipe(self, pipe_name, **kargs):
        if self.nlp.has_pipe(pipe_name):
            self.nlp.add_pipe(pipe_name, **kargs)
        else:
            logger.debug("pipe already in pipeline")


    def add_annotation_pipe(self, name, save:bool = False):
        cls, _ = utils.get_cls_from_path(Pipeline.ANNOTATORS_CONFIG["annotator"][name]["annotator_class"])
        instance = cls(Pipeline.ANNOTATORS_CONFIG, self.database_config)
        self.annotator_instances[name] = instance

        pipe_name = Pipeline.ANNOTATORS_CONFIG["annotator"][name]["pipe"]
        self.add_pipe(pipe_name)
        self.pipeline[name] = save

    def annotate(self, texts):
        self.annotated_text = list(self.nlp.pipe(texts, as_tuples=True))

    def save(self):
        if self.annotated_text is None:
            logger.error("call annotate before saving")
            pass
        for pipe, save in self.pipeline.items():
            if save:
                logger.info("saving annotations of {}".format(pipe))
                self.annotator_instances[pipe].save_annotations(self.annotated_text)


    @staticmethod
    def register_pipe(self, name:str, annotator_class_path:str):
        '''
        This function updates the ANNOTATOR-CLASS mapping It does not add the component to the pipeline, it registers it.
        Later you can add the {name} to the pipeline's list
        '''
        pass#Pipeline.ANNOTATOR_CLASS[name] = annotator_class_path
