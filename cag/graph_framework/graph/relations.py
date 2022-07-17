from pyArango.collection import Edges, Field

"""GENREAL EDGE DEFINITION WITH TIMESTAMP"""
class GenericEdge(Edges):
    _fields = {
        'timestamp': Field()
    }

"""GENERAL GRAPH EDGES"""
class BelongsTo(GenericEdge):
    _fields = GenericEdge._fields

class RefersTo(GenericEdge):
    _fields = GenericEdge._fields

class IsIdenticalTo(GenericEdge):
    _fields = GenericEdge._fields

class HasAuthor(GenericEdge):
    _fields = GenericEdge._fields

"""OPEN ALEX RELATED RELATIONS"""
class PublishedAt(GenericEdge):
    _fields = GenericEdge._fields