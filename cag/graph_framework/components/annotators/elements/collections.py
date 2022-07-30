


import cag.graph_framework.graph.nodes as parent_nodes
from cag.graph_framework.graph.relations import GenericEdge
from pyArango.collection import  Field

"""OOS NODES RELEVANT FOR ANNOTATIONS"""



class NamedEntityNode(parent_nodes.GenericNode):
    _fields = {
        "type": parent_nodes.Field(),
        "name": parent_nodes.Field(),
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensureFulltextIndex(["name"], name="fti_annotator_ner")
        self.ensurePersistentIndex(["name", "type"], unique=True)


class HasAnnotation(GenericEdge):
    _fields = {
        "count": Field(),
        "annotation_position": Field(), # array of tuples [(start, end), (start, end)]
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensurePersistentIndex(["_from", "_to"], unique=True)#, deduplicate=True)
