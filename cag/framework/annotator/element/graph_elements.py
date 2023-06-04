import cag.graph_elements.nodes as parent_nodes
from cag.graph_elements.relations import GenericEdge
from pyArango.collection import Field

"""OOS NODES RELEVANT FOR ANNOTATIONS"""


## NAMED ENTITY ANNOTATOR


class NamedEntityAnnotationNode(parent_nodes.GenericNode):
    """A class to define a Named Entity node in arangodb - This is used by pyarango to create the Collection"""

    _fields = {
        "type": parent_nodes.Field(),
        "name": parent_nodes.Field(),
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensureFulltextIndex(["name"], name="fti_annotator_ner")
        self.ensurePersistentIndex(["name", "type"], unique=True)


class GenericAnnotationNode(parent_nodes.GenericNode):
    """A class to define a Generic Annotation node in arangodb - This is used by pyarango to create the Collection"""

    _fields = {
        "label": parent_nodes.Field(),
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensurePersistentIndex(["label"], unique=True)


class EmpathAnnotationNode(GenericAnnotationNode):
    """A class to define a Empath node in arangodb - This is used by pyarango to create the Collection"""

    _fields = GenericAnnotationNode._fields


class EmotionAnnotationNode(GenericAnnotationNode):
    """A class to define a Emotion node in arangodb - This is used by pyarango to create the Collection"""

    _fields = GenericAnnotationNode._fields


class ToxicityAnnotationNode(GenericAnnotationNode):
    """A class to define a Toxicity node in arangodb - This is used by pyarango to create the Collection"""

    _fields = GenericAnnotationNode._fields


class MpqaAnnotationNode(GenericAnnotationNode):
    """A class to define a Mpqa node in arangodb - This is used by pyarango to create the Collection"""

    _fields = GenericAnnotationNode._fields


class HedgeAnnotationNode(GenericAnnotationNode):
    """A class to define a Hedge node in arangodb - This is used by pyarango to create the Collection"""

    _fields = GenericAnnotationNode._fields


class OAConceptAnnotationNode(parent_nodes.GenericNode):
    """A class to define a Named Entity node in arangodb - This is used by pyarango to create the Collection"""

    _fields = {
        "oa_id": parent_nodes.Field(),
        "name": parent_nodes.Field(),
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensureFulltextIndex(["oa_id", "name"], name="fti_annotator_oaconcept")
        self.ensurePersistentIndex(["oa_id", "name"], unique=True)

class MediaTopicAnnotationNode(parent_nodes.GenericNode):
    """A class to define a Named Entity node in arangodb - This is used by pyarango to create the Collection"""

    _fields = {
        "mediatopic_id": parent_nodes.Field(),
        "name": parent_nodes.Field(),
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensureFulltextIndex(["mediatopic_id", "name"], name="fti_annotator_mediatopic")
        self.ensurePersistentIndex(["mediatopic_id", "name"], unique=True)


class KeyTermAnnotationNode(parent_nodes.GenericNode):
    """A class to define a Named Entity node in arangodb - This is used by pyarango to create the Collection"""

    _fields = {
        "name": parent_nodes.Field(),
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensureFulltextIndex(["name"], name="fti_annotator_keyterm")
        self.ensurePersistentIndex(["name"], unique=True)

##############
#    EDGES   #
##############
class GenericAnnotationEdge(GenericEdge):
    """A class to define an annotation edge in arangodb - This is used by pyarango to create the Collection"""

    _fields = {
        "count": Field(default=0),
        "ratio": Field(default=0.0),
        "metadata": Field(),
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensurePersistentIndex(
            ["_from", "_to"], unique=True
        )  # , deduplicate=True)


class HasTokenLevelAnnotation(GenericAnnotationEdge):
    """This is an Edge for annotations on the token level"""

    _fields = {
        **GenericAnnotationEdge._fields,
        "token_position_lst": Field(
            default=None
        ),  # array of tuples [(start, end), (start, end)]
        "token_lst": Field(
            default=None
        ),  # array of tuples [(start, end), (start, end)]
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        self.ensurePersistentIndex(
            ["_from", "_to"], unique=True
        )  # , deduplicate=True)


# TODO: Below class is for backward compatibility - remove
class HasAnnotation(HasTokenLevelAnnotation):
    _fields = HasTokenLevelAnnotation._fields


class HasEmpathAnnotation(HasTokenLevelAnnotation):
    _fields = HasTokenLevelAnnotation._fields


class HasNERAnnotation(HasTokenLevelAnnotation):
    _fields = HasTokenLevelAnnotation._fields


class HasHedgeAnnotation(HasTokenLevelAnnotation):
    _fields = {
        **HasTokenLevelAnnotation._fields,
        "is_dominant": Field(default=False),
    }


class HasEmotionAnnotation(GenericAnnotationEdge):
    """A class to define an annotation edge in arangodb - This is used by pyarango to create the Collection"""

    _fields = {
        **GenericAnnotationEdge._fields,
        "mean_score": Field(default=0.0),
        "sentence_index_w_highest_score": Field(default=-1),
        "highest_score": Field(),
    }


class HasToxicityAnnotation(GenericAnnotationEdge):
    """A class to define an annotation edge in arangodb - This is used by pyarango to create the Collection"""

    _fields = {
        **GenericAnnotationEdge._fields,
        "mean_score": Field(default=0.0),
        "sentence_index_w_highest_score": Field(default=-1),
        "highest_score": Field(),
    }


class HasMpqaAnnotation(GenericAnnotationEdge):
    _fields = GenericAnnotationEdge._fields


class HasOAConceptAnnotation(GenericEdge):
    _fields = {
        **GenericEdge._fields,
        "level": Field(),
        "metadata": Field()
    }


class HasMediaTopicAnnotation(GenericEdge):
    _fields = {
        **GenericEdge._fields,
        "level": Field(),
        "metadata": Field()
    }


class HasKeyTermAnnotation(GenericEdge):
    _fields = {
        **GenericEdge._fields,
        "rank": Field(),
        "score": Field(),
        "metadata": Field()

    }
