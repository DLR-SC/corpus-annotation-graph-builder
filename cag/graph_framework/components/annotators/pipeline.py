import importlib

from typing import List, ClassVar
from pyArango.database import Database
from cag.utils import utils


class Pipeline:
    pipeline: dict
    database:Database

    def __post_init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.annotator_component_map = {}

        for pipe in self.pipeline:
            cls, class_name = utils.get_cls_from_path(Pipeline.ANNOTATOR_CLASS[pipe])
            instance = cls(self.database)
            self.annotator_component_map[pipe] = instance
            self.nlp.add_pipe(pipe)
        self.annotated_text = None


    def add_pipe(self, name, save:bool = False):
        if name in Pipeline.ANNOTATOR_CLASS.keys():
            self.pipeline[name] = save
        else:
            logger.error("the annotator was not added to the pipeline. Please register it first using the static"
                         "method: Pipeline.register_pipe(name: str, annotator_class_path:str )")
    def annotate(self, texts):
        self.annotated_text = list(self.nlp.pipe(texts))

    def save(self):
        if self.annotated_text is None:
            logger.error("call annotate before saving")
            pass
        for pipe, save in self.pipeline.items():
            if save:
                logger.info("saving annotations of {}".format(pipe))
                self.annotator_component_map[pipe].save(self.annotated_text)


    #### ANNOTATORS  CONSTANTS ###

    ## ADD THE KEY AS BELOW

    NAMED_ENTITY: ClassVar = "ner"
    ARGUING_LEXICON: ClassVar = "mpqa_parser"
    ARGUING_LEXICON_COUNTER: ClassVar = "mpqa_counter"
    EMPATH : ClassVar = "empath_component"

    ## ADD THE CORRESPONDING class path for each key - this will initaitate it and create the Collection
    ANNOTATOR_CLASS: ClassVar = {NAMED_ENTITY: "cag.annotators.named_entity_annotator.NamedEntityAnnotator",
                                 EMPATH: None}


    @staticmethod
    def register_pipe(self, name:str, annotator_class_path:str):
        '''
        This function updates the ANNOTATOR-CLASS mapping It does not add the component to the pipeline, it registers it.
        Later you can add the {name} to the pipeline's list
        '''
        Pipeline.ANNOTATOR_CLASS[name] = annotator_class_path
