from abc import ABC, abstractmethod

from cag import logger

from cag.utils.config import Config

from cag.framework.component import Component
from datetime import datetime


class GraphCreatorBase(ABC, Component):

    #### Constant NODE and Edge NAMES ####
    _TEXT_NODE_NAME = 'TextNode'
    _WEB_RESOURCE_NODE_NAME = 'WebResource'
    _AUTHOR_NODE_NAME = 'Author'
    _CORPUS_NODE_NAME = 'Corpus'
    _IMAGE_NODE_NAME = 'ImageNode'
    _DATA_NODE_NAME = 'DataNode'
    _KEY_TERM_NODE_NAME = 'KeyTerm'
    _ABSTRACT_NODE_NAME = 'Abstract'

    _BELONGS_TO_RELATION_NAME = 'BelongsTo'
    _REFERS_TO_RELATION_NAME = 'RefersTo'
    _HAS_AUTHOR_RELATION_NAME = 'HasAuthor'
    _PUBLISHED_AT_RELATION_NAME = 'PublishedAt'
    _EDGE_ABSTRACT_TEXT = 'AbstractText'
    _EDGE_TEXT_TERM = 'TextTerm'
    _EDGE_KEYTERM_RELATION = 'KeyTermRelation'

    _COMPONENT_NAME = 'Graph Creator'
    _base_edge_definitions = [
        {
            'relation': _EDGE_ABSTRACT_TEXT,
            'from_collections': [_ABSTRACT_NODE_NAME],
            'to_collections': [_TEXT_NODE_NAME]
        },
        {
            'relation': _EDGE_TEXT_TERM,
            'from_collections': [_TEXT_NODE_NAME],
            'to_collections': [_KEY_TERM_NODE_NAME]
        },
        {
            'relation': _EDGE_KEYTERM_RELATION,
            'from_collections': [_KEY_TERM_NODE_NAME],
            'to_collections': [_KEY_TERM_NODE_NAME]
        }
    ]

    def __init__(self, corpus_file_or_dir: str, conf: Config = None, initialize=False, load_generic_graph=True):
        """Creates a graph and provides some general helper methods

        :param corpus_file_or_dir: where your update_graph-method can find it's data 
        :type corpus_file_or_dir: str
        :param conf: config+connection to DB, defaults to None
        :type conf: Config, optional
        :param initialize: whether to initaialze the DB using init_graph(), defaults to False
        :type initialize: bool, optional
        :type load_generic_graph: bool, optional whether to load the predefined nodes and relations
        """
        if not load_generic_graph:
            self._base_edge_definitions = []
        super().__init__(conf)
        self.corpus_file_or_dir = corpus_file_or_dir
        self.now = datetime.now()
        if initialize:
            self.init_graph()

    @abstractmethod
    def init_graph(self):
        g = self.graph

    def update_graph(self, timestamp):
        g = self.graph

    ######### END OF HELPERS ###########################################################

    ######### Generic func to create vertices ##########################################

    def create_corpus_node(self, key, name, type, desc, created_on, timestamp=None):

        dict_ = {
            "_key": key,
            "name": name,
            "type": type,
            "description": desc,
            "created_on": created_on,
            "timestamp": timestamp
        }
        corpus = self.upsert_node(GraphCreatorBase._CORPUS_NODE_NAME, dict_)
        return corpus

    def create_text_node(self, text, timestamp=None):

        dict_ = {
            "text": text,
            "timestamp": timestamp
        }

        txt = self.upsert_node(
            GraphCreatorBase._TEXT_NODE_NAME, dict_, alt_key="text")
        return txt

    def create_image_node(self, url, timestamp=None):

        dict_ = {
            "url": url,
            "timestamp": timestamp
        }

        img = self.upsert_node(
            GraphCreatorBase._IMAGE_NODE_NAME,  dict_, alt_key="url")
        return img

    def create_author_node(self, author_name, timestamp=None):

        dict_ = {
            "name": author_name,
            "timestamp": timestamp
        }

        author = self.upsert_node(
            GraphCreatorBase._AUTHOR_NODE_NAME, dict_, alt_key="name")

        return author

    def create_web_resource_node(self, url, timestamp=None):

        dict_ = {
            "url": url,
            "timestamp": timestamp
        }

        web_resource = self.upsert_node(
            GraphCreatorBase._WEB_RESOURCE_NODE_NAME, dict_, alt_key="url")
        return web_resource
