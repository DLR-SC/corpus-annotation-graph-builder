


import cag.graph_elements.nodes as parent_nodes
from cag.graph_elements.relations import GenericEdge
from pyArango.collection import  Field

"""OOS NODES RELEVANT FOR ANNOTATIONS"""


## NAMED ENTITY ANNOTATOR

class NamedEntityNode(parent_nodes.GenericNode):
    """ A class to define a Named Entity node in arangodb - This is used by pyarango to create the Collection """
    _fields = {
        "type": parent_nodes.Field(),
        "name": parent_nodes.Field(),
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensureFulltextIndex(["name"], name="fti_annotator_ner")
        self.ensurePersistentIndex(["name", "type"], unique=True)


class EmpathNode(parent_nodes.GenericNode):
    """ A class to define a Named Entity node in arangodb - This is used by pyarango to create the Collection """
    _fields = {
        "category": parent_nodes.Field(),
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensureFulltextIndex(["category"], name="fti_annotator_empath")
        self.ensurePersistentIndex(["category"], unique=True)

class HasAnnotation(GenericEdge):
    """ A class to define an annotation edge in arangodb - This is used by pyarango to create the Collection """

    _fields = {
        "count": Field(),
        "ratio": Field(),
        "token_position_lst": Field(), # array of tuples [(start, end), (start, end)]
        "token_lst": Field(),  # array of tuples [(start, end), (start, end)]
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensurePersistentIndex(["_from", "_to"], unique=True)#, deduplicate=True)
