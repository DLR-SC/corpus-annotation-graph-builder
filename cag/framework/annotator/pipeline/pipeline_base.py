from queue import Queue
from abc import ABC, abstractmethod
from typing import ClassVar

import dataclasses
from spacy import Language

import spacy
from tqdm import tqdm

from cag import logger
from cag.framework.annotator import registered_pipes
from cag.framework.annotator.element.orchestrator import PipeOrchestrator
from cag.utils import utils


@dataclasses.dataclass
class Pipe:
    name: str
    save_output: bool = True
    is_spacy:bool = False
    is_native:bool = False
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
                 input = None,
                 load_default_pipe_configs = True,
                 extended_pipe_configs:dict = None,
                 save_output= False,
                 out_path = None
                 ):
        """
        The Pipeline class is responsible for taking a set of nodes as input, annotating them and saving them into
        the database.

        """

        self.registered_pipes = self._load_registered_pipes(load_default_pipe_configs, extended_pipe_configs)
        self.save_output = save_output
        self.out_path = out_path

        self.pipe_instance_dict = {}
        self.pipeline:list = []


        self.processed_input = None
        self.set_input(input)

        self.annotated_artifacts = None
        self.out_df = None

        self.set_spacy_language_model()
        self.pipe_stacks = None
        self.stack = []
        self.spacy_n_processors = 1

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
    def init_pipe_stack(self):
        self.pipe_stacks = self.get_pipe_stacks()
        self.stack =[]
        while not self.pipe_stacks.empty():
            pipe_stack = self.pipe_stacks.get()
            if pipe_stack['stack_type'] == 'spacy':
                nlp = self.init_spacy_nlp(pipe_stack['stack'])
                self.stack.append({"type": "spacy", "component": nlp})
                #out = list(nlp.pipe(input, as_tuples=True, n_process=-1, batch_size=3000))
                #input = out
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
                        self.stack.append({"type": "default", "component": pipe_func})
        logger.debug(f"The stack has {len(self.stack)} component(s).")
        return self.stack
                        #out = pipe_func(input)
                        #input = out
        #self.annotated_artifacts = out
    def annotate(self):
        input = self.processed_input
        logger.debug("Annotating - looping over stack")
        for s in self.stack:
            logger.debug(f"executing component of type {s['type']} ")
            _component = s['component']
            if s['type'] == 'spacy':
                if self.spacy_n_processors != 1:
                    logger.info(f"In case you are using transformer based pipe, set *spacy_n_processors* to 1 instead of {self.spacy_n_processors } or else the nlp.pipe will freeze")
                out = list(s['component'].pipe(input, as_tuples=True, n_process=self.spacy_n_processors ))
                input = out
            else:
                out = _component(input)
                input = out
        logger.debug("Ran all stack components")
        self.annotated_artifacts = out


    def save(self):
        logger.debug("Saving annotations..")
        if self.annotated_artifacts is None:
            logger.error("Nothing to save, call annotate before saving")
            pass
        for pipe in tqdm(self.pipeline):
            if pipe.save_output:
                logger.info("saving annotations of {}".format(pipe))
                if self.out_df is None:
                    self.out_df = self.pipe_instance_dict[pipe.name].save_annotations(self.annotated_artifacts)
                else:
                    _df = self.pipe_instance_dict[pipe.name].save_annotations(self.annotated_artifacts)
                    self.out_df = self.out_df.merge(_df,
                                                    how='outer',
                                                    left_on="input_id",
                                                    right_on="input_id")
        if self.save_output:
            logger.debug("Saving to parquet..")
            self.out_df.to_parquet(self.out_path)
        logger.debug("saved annotations")

    ############################################
    #####           SETTERS                #####
    ############################################
    def reset_input_output(self):
        self.set_input(None)
        self.annotated_artifacts = None

    def set_input(self, nodes):
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
                            name:str="", save_output: bool = False,
                            is_spacy:bool=False, is_native: bool = False):
        """
            The add_annotation_pipe adds a pipe to the pipeline. the pipes are first in first out (FIFO).
            The corrisponding Annotator class (given from the toml)  to this pipe is initiated and saved, to be used
            for annotating and saving to the database.
            *annotator_instances*
            *pipe_id_or_func*
            *pipeline*
        """
        pipe = pipe if pipe is not None else Pipe(name, save_output, is_spacy, is_native)

        if is_native and is_spacy and not save_output:
            pipe.pipe_id_or_func = name
            self.pipeline.append(pipe)
            return

        logger.info(f"adding pipe with name {pipe.name}")
        cls, _ = utils.get_cls_from_path(self.registered_pipes[pipe.name][registered_pipes.PipeConfigKeys._orchestrator_class])
        instance = cls(self.registered_pipes, orchestrator_config_id= pipe.name)
        self.pipe_instance_dict[pipe.name] = instance

        logger.info(f"adding pipe with code {instance.pipe_id_or_func}")
        pipe.pipe_id_or_func = instance.pipe_id_or_func

        self.pipeline.append(pipe)

    ############################################
    #####       HELPER METHODS             #####
    ############################################
    def get_pipe_stacks(self):
        logger.info("Defining pipe default and spacy stacks")
        pipe_queue: list = self.pipeline.copy()
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
        nlp:Language =  spacy.blank("en")#spacy.load(self.spacy_language_model, exclude=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"])
        for pipe in subpipeline:
            if not nlp.has_pipe(pipe.pipe_id_or_func):
                if pipe.pipe_id_or_func in nlp.disabled:
                    nlp.enable_pipe(pipe.pipe_id_or_func)
                else:
                    nlp.add_pipe(pipe.pipe_id_or_func)#, **kargs)
            else:
                logger.debug("pipe already in pipeline")
        logger.info(f"Pipes are {nlp.pipe_names}")
        return nlp

    def load_spacy_model(self):
        if not spacy.util.is_package(self.spacy_language_model):
            spacy.cli.download(self.spacy_language_model)