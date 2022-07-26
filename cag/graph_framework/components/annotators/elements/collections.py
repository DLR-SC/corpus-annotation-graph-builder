


import cag.graph_framework.graph.nodes as parent_nodes
from cag.graph_framework.graph.relations import GenericEdge
from pyArango.collection import Collection, Field

"""OOS NODES RELEVANT FOR ANNOTATIONS"""



class NamedEntityNode(parent_nodes.GenericNode):
    _fields = {
        "type": parent_nodes.Field(),
        "name": parent_nodes.Field(),
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensureFulltextIndex(["name"])
        self.ensurePersistentIndex(["name", "type"])


class HasAnnotation(GenericEdge):
    _fields = {
        "count": Field(),
        "annotation_position": Field(), # array of tuples [(start, end), (start, end)]

    }
