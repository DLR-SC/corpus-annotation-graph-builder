from pyArango.collection import Collection, Field

"""BASE NODES (OOS nodes and Annotations)"""


class GenericNode(Collection):
    _fields = Collection._fields


class GenericOOSNode(Collection):
    _fields = {"timestamp": Field()}


class AnnotationNode(Collection):
    _fields = {"timestamp": Field(), "parameters": Field()}


"""GENERAL OOS NODES"""


class Corpus(GenericOOSNode):

    _fields = {
        "name": Field(),
        "type": Field(),
        "description": Field(),
        "created_on": Field(),
        **GenericOOSNode._fields,
    }


class ImageNode(GenericOOSNode):
    _fields = {"url": Field(), **GenericOOSNode._fields}


class DataNode(GenericOOSNode):
    _fields = {"url": Field(), **GenericOOSNode._fields}


class TextNode(GenericOOSNode):
    _fields = {"text": Field(), **GenericOOSNode._fields}


class Author(GenericOOSNode):
    _fields = {"name": Field(), **GenericOOSNode._fields}


class KeyTerm(GenericOOSNode):
    _fields = {"name": Field(), **GenericOOSNode._fields}


class AbstractNode(GenericOOSNode):
    _fields = {"text": Field(), **GenericOOSNode._fields}


class WebResource(GenericOOSNode):
    _fields = {"url": Field(), **GenericOOSNode._fields}
