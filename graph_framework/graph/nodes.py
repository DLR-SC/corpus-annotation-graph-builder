from pyArango.collection import Collection, Field

"""BASE NODES (OOS nodes and Annotations)"""


class GenericNode(Collection):
    _fields = Collection._fields


class GenericOOSNode(Collection):
    _fields = {
        'timestamp': Field()
    }


class AnnotationNode(Collection):
    _fields = {
        'timestamp': Field(),
        'parameters': Field()
    }


"""GENERAL OOS NODES"""


class Corpus(GenericOOSNode):

    _fields = {
        'name': Field(),
        'type': Field(),
        'description': Field(),
        'created_on': Field(),
        **GenericOOSNode._fields
    }


class ImageNode(GenericOOSNode):
    _fields = {
        "url": Field(),
        **GenericOOSNode._fields
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        # TODO: see above
        #self.ensurePersistentIndex(["url"], unique=True)


class DataNode(GenericOOSNode):
    _fields = {
        "url": Field(),
        **GenericOOSNode._fields
    }


class TextNode(GenericOOSNode):
    _fields = {
        "text": Field(),
        **GenericOOSNode._fields
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        #TODO @Roxanne: please do not modify general nodes to specific application, move this code to a special node
        #self.ensureFulltextIndex(["text"])
        #self.ensureHashIndex(["text"], unique=True)


class Author(GenericOOSNode):
    _fields = {
        "name": Field(),
        **GenericOOSNode._fields
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        #TODO: see above
        #self.ensurePersistentIndex(["name"], unique=True)


class KeyTerm(GenericOOSNode):
    _fields = {
        "name": Field(),
        **GenericOOSNode._fields
    }


class AbstractNode(GenericOOSNode):
    _fields = {
        "text": Field(),
        **GenericOOSNode._fields
    }


"""OOS NODES RELEVANT FOR WIKIPEDIA CORPUS"""


class WikiArticle(GenericOOSNode):
    _fields = {
        "name": Field(),
        "lang": Field(),
        "is_popular": Field(),
        "is_important": Field(),
        **GenericOOSNode._fields
    }


class WikiArticleRevision(GenericOOSNode):
    _fields = {
        'rev_id': Field(),
        'rev_timestamp': Field(),
        **GenericOOSNode._fields
    }


class WikiArticleSection(GenericOOSNode):
    _fields = {
        'name': Field(),
        **GenericOOSNode._fields
    }


"""OOS NODES RELEVANT FOR WIKIPEDIA CORPUS"""


class WebResource(GenericOOSNode):
    _fields = {
        'url': Field(),
        **GenericOOSNode._fields
    }

    def __init__(self, database, jsonData):
        super().__init__(database, jsonData)
        #TODO: see..
        #self.ensurePersistentIndex(["url"], unique=True)
