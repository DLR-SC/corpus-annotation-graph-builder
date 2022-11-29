import dataclasses
from typing import ClassVar

_dict = {}

########## Dictionary Keys ##########
@dataclasses.dataclass
class PipeConfigKeys:
    _orchestrator_class : ClassVar = "orchestrator_class"
    _pipe_id_or_func : ClassVar = "pipe_id_or_func"
    _pipe_path : ClassVar = "pipe_path"  # leave empty if the pipe is a spacy native pipe
    _level : ClassVar = "level"  # node or set
    _data_type : ClassVar = "data_type"  # for now we support text - later url, image
    _annotated_column : ClassVar = "annotated_column"
    _input_id : ClassVar = "input_id"
    _vertex_class : ClassVar = "vertex_class"
    _edge_class : ClassVar ="edge_class"
    _annotated_vertex_name : ClassVar = "annotated_vertex_name"



_dict["NamedEntityPipeOrchestrator"] = {
    PipeConfigKeys._orchestrator_class : "cag.graph_framework.components.annotators.instance.ner_orchestrator.NamedEntityPipeOrchestrator",
    PipeConfigKeys._pipe_id_or_func : "ner", # id in case of space, function name otherwise
    PipeConfigKeys._pipe_path : "",  # leave empty if the pipe is a spacy native pipe, otherwise provide the path of where the pipe_id_or_func exists
    PipeConfigKeys._level : "node",  # node or set
    PipeConfigKeys._data_type : "text",  # for now we support text - later url, image
    PipeConfigKeys._annotated_vertex_name : "TextNode",
    PipeConfigKeys._vertex_class : "cag.graph_framework.components.annotators.element.graph_elements.NamedEntityNode",
    PipeConfigKeys._edge_class : "cag.graph_framework.components.annotators.element.graph_elements.HasAnnotation"
}


_dict["EmpathPipeOrchestrator"] = {
    PipeConfigKeys._orchestrator_class : "cag.graph_framework.components.annotators.instance.empath_orchestrator.EmpathPipeOrchestrator",
    PipeConfigKeys._pipe_id_or_func : "empath_component", # id in case of space, function name otherwise
    PipeConfigKeys._pipe_path : "cag.graph_framework.components.annotators.pipe.linguistic.style_features",  # leave empty if the pipe is a spacy native pipe, otherwise provide the path of where the pipe_id_or_func exists
    PipeConfigKeys._level : "node",  # node or set
    PipeConfigKeys._data_type : "text",  # for now we support text - later url, image
    PipeConfigKeys._annotated_vertex_name : "TextNode",
    PipeConfigKeys._vertex_class : "cag.graph_framework.components.annotators.element.graph_elements.EmpathNode",
    PipeConfigKeys._edge_class : "cag.graph_framework.components.annotators.element.graph_elements.HasAnnotation"
}

_dict["DummyPipeOrchestrator"] = {
    PipeConfigKeys._orchestrator_class : "cag.graph_framework.components.annotators.instance.dummy.DummyPipeOrchestrator",
    PipeConfigKeys._pipe_id_or_func : "customized_pipe_func", # id in case of space, function name otherwise
    PipeConfigKeys._pipe_path : "cag.graph_framework.components.annotators.instance.dummy",  # leave empty if the pipe is a spacy native pipe, otherwise provide the path of where the pipe_id_or_func exists
    PipeConfigKeys._level : "node",  # node or set
    PipeConfigKeys._data_type : "text",  # for now we support text - later url, image
    PipeConfigKeys._annotated_vertex_name : "TextNode",
    PipeConfigKeys._vertex_class : "cag.graph_framework.graph.nodes.GenericNode",
    PipeConfigKeys._edge_class : "cag.graph_framework.components.annotators.element.graph_elements.HasAnnotation"
}