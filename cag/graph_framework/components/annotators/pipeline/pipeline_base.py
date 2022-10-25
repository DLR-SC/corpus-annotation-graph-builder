from queue import Queue
from abc import ABC, abstractmethod
from typing import ClassVar

import dataclasses
from pyArango.collection import Collection
from spacy import Language

from cag import logger
from cag.graph_framework.components.annotators import registered_pipes
from cag.graph_framework.components.annotators.element.orchestrator import PipeOrchestrator
from cag.utils import utils
import spacy
from tqdm import tqdm
from cag.utils.config import Config

@dataclasses.dataclass
class Pipe:
    name: str
    is_spacy:bool = False
    save_output:bool = True
    pipe_id_or_func:str = None # set internally from toml




class Pipeline(ABC):
    REGISTERED_PIPE_CONFIGS: ClassVar = registered_pipes._dict

    def _load_registered_pipes(self, load_default_pipe_configs:bool = True,
                 extended_pipe_configs:dict = None):
        if load_default_pipe_configs:
            _copy = Pipeline.REGISTERED_PIPE_CONFIGS.copy()
            if  extended_pipe_configs is not None:
                _copy.update(extended_pipe_configs)
            registered_pipes = _copy
        return registered_pipes
    def __init__(self,
                 database_config: Config,
                 input: "[Collection]" = None,
                 load_default_pipe_configs = True,
                 extended_pipe_configs:dict = None
                 ):
        """
        The Pipeline class is responsible for taking a set of nodes as input, annotating them and saving them into
        the database.

        """

        self.registered_pipes = self._load_registered_pipes(load_default_pipe_configs, extended_pipe_configs)

        self.pipe_instance_dict = {}
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
    def init_and_run(self) -> list:
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
                    pipe_instance :PipeOrchestrator = self.pipe_instance_dict[current_pipe.name]
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
            logger.error("Nothing to save, call annotate before saving")
            pass
        for pipe in tqdm(self.pipeline):
            if pipe.save_output:
                logger.info("saving annotations of {}".format(pipe))
                self.pipe_instance_dict[pipe.name].save_annotations(self.annotated_artifacts)


    ############################################
    #####           SETTERS                #####
    ############################################
    def reset_input_output(self):
        self.set_input(None)
        self.annotated_artifacts = None

    def set_input(self, nodes: [Collection]):
        self.input = nodes
        if self.input is not None:
            self.processed_input = self.process_input()
        else:
            self.processed_input = None

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
            *pipe_id_or_func*
            *pipeline*
        """
        pipe = pipe if pipe is not None else Pipe(name, save_output, is_spacy)

        logger.info(f"adding pipe with name {pipe.name}")
        cls, _ = utils.get_cls_from_path(self.registered_pipes[pipe.name][registered_pipes.PipeConfigKeys._orchestrator_class])
        instance = cls(self.registered_pipes, orchestrator_config_id= pipe.name, conf=self.database_config)
        self.pipe_instance_dict[pipe.name] = instance

        logger.info(f"adding pipe with code {instance.pipe_id_or_func}")
        pipe.pipe_id_or_func = instance.pipe_id_or_func

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
            if not nlp.has_pipe(pipe.pipe_id_or_func):
                if pipe.pipe_id_or_func in nlp.disabled:
                    nlp.enable_pipe(pipe.pipe_id_or_func)
                else:
                    nlp.add_pipe(pipe.pipe_id_or_func)#, **kargs)
            else:
                logger.debug("pipe already in pipeline")
        return nlp

    def load_spacy_model(self):
        if not spacy.util.is_package(self.spacy_language_model):
            spacy.cli.download(self.spacy_language_model)


