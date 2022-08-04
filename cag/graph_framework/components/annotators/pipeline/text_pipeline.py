import os
from pathlib import Path
from typing import ClassVar

import tomli

from cag import logger
from cag.graph_framework.components.annotators.pipeline.pipeline_base import Pipeline
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
def load_spacy_model(language_package):
    if not spacy.util.is_package(language_package):
        spacy.cli.download(language_package)

config_path = os.path.join("configs", "annotator.toml")



class TextPipeline(Pipeline):
    """
    The TextPipeline is a Pipeline that is meant to deal with node(s) with textual content.
    It uses the spacy pipeline to conduct the annotations. I can use spacy pipes or customized pipes
    The goal of this pipeline is to take a set of nodes as input, annotate them and save them into the database.
    """
    TYPE: ClassVar = "TEXT"

    def __init__(self, database_config: Config,
                 pipeline: dict = {},
                 language_package=SPACY_LANGUAGE_PACKAGE["en_sm"],
                ):
        super().__init__(  TextPipeline.TYPE, database_config, pipeline)

        self.language_package = language_package
        load_spacy_model(self.language_package)
        self.nlp = spacy.load(self.language_package, disable=["ner"])
        #self.nlp.remove_pipe('ner')

    def add_pipe(self, pipe_name, **kargs):
        logger.info('adding pipe in textpipeline')
        if not self.nlp.has_pipe(pipe_name):
            if pipe_name in self.nlp.disabled:
                self.nlp.enable_pipe(pipe_name)
            else:
                self.nlp.add_pipe(pipe_name, **kargs)
        else:
            logger.debug("pipe already in pipeline")

    def annotate(self, texts):
        self.annotated_artifacts = list(self.nlp.pipe(texts, as_tuples=True))

