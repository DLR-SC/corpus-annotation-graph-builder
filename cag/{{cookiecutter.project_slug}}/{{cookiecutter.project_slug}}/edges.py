from cag.graph_elements.relations import GenericEdge
from pyArango.collection import Field


class PlayedIn(GenericEdge):
    """
    A class representing a 'played in' edge in a graph.

    Inherits from GenericEdge class.

    Attributes:
        _fields (dict): A dictionary containing the fields and their respective types for the 'played in' edge.
    """
    _fields = {"rating": Field(), **GenericEdge._fields}


class Directed(GenericEdge):
    """
    A class representing a 'directed' edge in a graph.

    Inherits from GenericEdge class.
    """
    ...
