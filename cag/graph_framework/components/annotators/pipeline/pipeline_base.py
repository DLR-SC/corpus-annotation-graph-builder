import os
from collections import deque
from queue import Queue
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

import dataclasses
import tomli
from pyArango.collection import Collection
from spacy import Language

from cag import logger
from cag.graph_framework.components.annotators.element.annotator import Annotator
from cag.utils import utils
import spacy

from cag.utils.config import Config

config_path = os.path.join("configs", "annotator.toml")


@dataclasses.dataclass
class Pipe:
    name: str
    is_spacy:bool = False
    save_output:bool = True
    pipe_code:str = None # set internally from toml




class Pipeline(ABC):
    ANNOTATORS_CONFIG: ClassVar = tomli.loads(
        Path(config_path).read_text(encoding="utf-8"))  # default call annotators.get_annotators_config


    def __init__(self,
                 database_config: Config,
                 input: "[Collection]" = None):
        """
        The Pipeline class is responsible for taking a set of nodes as input, annotating them and saving them into
        the database.

        """
        self.annotator_instances = {}
        self.pipeline:[Pipe] = []


        self.database_config = database_config

        self.processed_input = None
        self.set_input(input)

        self.annotated_artifacts = None

        self.set_spacy_language_model()

    ############################################
    #####      ABSTRACT METHODS            #####
    ############################################
    @abstractmethod
    def process_input(self) -> object:

        pass

    @abstractmethod
    def instanciate_and_run(self) -> list:
        pass
    ############################################
    #####      MAIN. ANNOTATE and SAVE     #####
    ############################################

    def annotate(self):
        pipe_stacks = self.get_pipe_stacks()
        input = self.processed_input
        out = None
        while not pipe_stacks.empty():
            pipe_stack = pipe_stacks.get()
            if pipe_stack['stack_type'] == 'spacy':
                nlp = self.init_spacy_nlp(pipe_stack['stack'])
                out = list(nlp.pipe(input, as_tuples=True))
                input = out
            else:
                while pipe_stack['stack']:
                    current_pipe: Pipe = pipe_stack['stack'].pop(0)
                    pipe_instance :Annotator = self.annotator_instances[current_pipe.name]
                    pipe_func = pipe_instance.get_pipe_func()
                    if pipe_func is None:
                        logger.error("The pipe is not a spacy pipe. Make sure to define the pipe_path and pipe code and "
                                     "provide the implementation within the pipe path and a function with the name equivalent to the "
                                     "'pipe' name")
                    else:
                        out = pipe_func(input)
                        input = out
        self.annotated_artifacts = out


    def save(self):
        if self.annotated_artifacts is None:
            logger.error("call annotate before saving")
            pass
        for pipe in self.pipeline:
            if pipe.save_output:
                logger.info("saving annotations of {}".format(pipe))
                self.annotator_instances[pipe.name].save_annotations(self.annotated_artifacts)


    ############################################
    #####           SETTERS                #####
    ############################################

    def set_input(self, nodes: [Collection]):
        self.input = nodes
        if self.input is not None:
            self.processed_input = self.process_input()

    def set_spacy_language_model(self, language_package = "en_core_web_sm"):
        self.spacy_language_model = language_package
        self.load_spacy_model()
        # English pipeline optimized for CPU. Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer:
        #   en_core_web_sm (12MB)
        #   en_core_web_md (31MB)
        #   en_core_web_lg (382MB)
        # English transformer pipeline (roberta-base). Components: transformer, tagger, parser, ner, attribute_ruler, lemmatizer.
        #   en_core_web_trf (438)




    def add_annotation_pipe(self, pipe:Pipe=None,
                            name:str="", save_output: bool = False, is_spacy:bool=False):
        """
            The add_annotation_pipe adds a pipe to the pipeline. the pipes are first in first out (FIFO).
            The corrisponding Annotator class (given from the toml)  to this pipe is initiated and saved, to be used
            for annotating and saving to the database.
            *annotator_instances*
            *pipe_code*
            *pipeline*
        """
        pipe = pipe if pipe is not None else Pipe(name, save_output, is_spacy)

        logger.info(f"adding pipe with name {pipe.name}")
        cls, _ = utils.get_cls_from_path(Pipeline.ANNOTATORS_CONFIG["annotator"][pipe.name]["annotator_class"])
        instance = cls(Pipeline.ANNOTATORS_CONFIG, self.database_config)
        self.annotator_instances[pipe.name] = instance

        logger.info(f"adding pipe with code {instance.pipe_code}")
        pipe.pipe_code = instance.pipe_code

        self.pipeline.append(pipe)

    ############################################
    #####       HELPER METHODS             #####
    ############################################
    def get_pipe_stacks(self):
        logger.info("Defining pipe default and spacy stacks")
        pipe_queue: [Pipe] = self.pipeline.copy()
        pipe_stack: Queue = Queue()  # {"spacy": ["ner", "bla", "bloo], "default": ["da", "doo", "di"}
        task_collection = []
        previous_task_is_spacy = False
        while pipe_queue:
            current: Pipe = pipe_queue.pop(0) # Fifo
            current_is_spacy = current.is_spacy
            if (previous_task_is_spacy == current_is_spacy) or len(task_collection) == 0:
                task_collection.append(current)
            else:
                stack_type = "spacy" if previous_task_is_spacy else "default"
                pipe_stack.put({'stack_type': stack_type, 'stack': task_collection})
                task_collection = [current]
            previous_task_is_spacy = current_is_spacy

        if len(task_collection) > 0:
            stack_type = "spacy" if previous_task_is_spacy else "default"
            pipe_stack.put({'stack_type': stack_type, 'stack': task_collection})


        return pipe_stack

    def init_spacy_nlp(self, subpipeline) -> Language:
        nlp = spacy.load(self.spacy_language_model, disable=["ner"])
        for pipe in subpipeline:
            if not nlp.has_pipe(pipe.pipe_code):
                if pipe.pipe_code in nlp.disabled:
                    nlp.enable_pipe(pipe.pipe_code)
                else:
                    nlp.add_pipe(pipe.pipe_code)#, **kargs)
            else:
                logger.debug("pipe already in pipeline")
        return nlp

    def load_spacy_model(self):
        if not spacy.util.is_package(self.spacy_language_model):
            spacy.cli.download(self.spacy_language_model)
    ############################################
    #####    static. TOML EXTENSION        #####
    ############################################

    @staticmethod
    def extend_annotators(extended_config_dict_or_path: "dict|str" = None):
        config = tomli.loads(Path(config_path).read_text(encoding="utf-8"))
        if type(extended_config_dict_or_path) == str:
            extended_dic = tomli.loads(
                Path(extended_config_dict_or_path).read_text(encoding="utf-8"))
        else:
            extended_dic = extended_config_dict_or_path
        if extended_dic is not None:
            config.update(extended_dic)
        Pipeline.ANNOTATORS_CONFIG = config
        return config


