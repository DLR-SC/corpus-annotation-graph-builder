from abc import ABC, abstractmethod

from cag import logger

from cag.utils.config import Config

from cag.framework.component import Component
from datetime import datetime
from cag.graph_elements.nodes import (
    TextNode,
    WebResource,
    Author,
    Corpus,
    ImageNode,
    DataNode,
    KeyTerm,
    AbstractNode,
    IFrameNode,
    VideoNode,
)
from cag.graph_elements.relations import (
    BelongsTo,
    RefersTo,
    HasAuthor,
    PublishedAt,
    HasAbstract,
    HasTerm,
    KeyTermRelation,
)


class GraphCreatorBase(ABC, Component):
    # constant NODE and Edge NAMES ####
    _TEXT_NODE_NAME = TextNode.__name__
    _WEB_RESOURCE_NODE_NAME = WebResource.__name__
    _AUTHOR_NODE_NAME = Author.__name__
    _CORPUS_NODE_NAME = Corpus.__name__
    _IMAGE_NODE_NAME = ImageNode.__name__
    _DATA_NODE_NAME = DataNode.__name__
    _KEY_TERM_NODE_NAME = KeyTerm.__name__
    _ABSTRACT_NODE_NAME = AbstractNode.__name__

    _BELONGS_TO_RELATION_NAME = BelongsTo.__name__
    _REFERS_TO_RELATION_NAME = RefersTo.__name__
    _HAS_AUTHOR_RELATION_NAME = HasAuthor.__name__
    _PUBLISHED_AT_RELATION_NAME = PublishedAt.__name__
    _EDGE_ABSTRACT_TEXT = HasAbstract.__name__
    _EDGE_TEXT_TERM = HasTerm.__name__
    _EDGE_KEYTERM_RELATION = KeyTermRelation.__name__

    _COMPONENT_NAME = "Graph Creator"
    _base_edge_definitions = [
        {
            "relation": _EDGE_ABSTRACT_TEXT,
            "from_collections": [_ABSTRACT_NODE_NAME],
            "to_collections": [_TEXT_NODE_NAME],
        },
        {
            "relation": _EDGE_TEXT_TERM,
            "from_collections": [_TEXT_NODE_NAME],
            "to_collections": [_KEY_TERM_NODE_NAME],
        },
        {
            "relation": _EDGE_KEYTERM_RELATION,
            "from_collections": [_KEY_TERM_NODE_NAME],
            "to_collections": [_KEY_TERM_NODE_NAME],
        },
    ]

    def __init__(
        self,
        corpus_file_or_dir: str,
        conf: Config = None,
        initialize=False,
        load_generic_graph=True,
    ):
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

    def create_corpus_node(
        self,
        key,
        name,
        type,
        desc,
        created_on,
        timestamp=None,
        lang=None,
        copyright=None,
    ):
        dict_ = {
            "_key": key,
            "name": name,
            "type": type,
            "description": desc,
            "created_on": created_on,
            "timestamp": timestamp,
            "lang": lang,
            "copyright": copyright,
        }
        corpus = self.upsert_node(GraphCreatorBase._CORPUS_NODE_NAME, dict_)
        return corpus

    def create_text_node(self, text, timestamp=None):
        dict_ = {"text": text, "timestamp": timestamp}

        txt = self.upsert_node(
            GraphCreatorBase._TEXT_NODE_NAME, dict_, alt_key="text"
        )
        return txt

    def create_image_node(self, url, copyright=None, timestamp=None):
        dict_ = {"url": url, "timestamp": timestamp, "copyright": copyright}

        img = self.upsert_node(
            GraphCreatorBase._IMAGE_NODE_NAME, dict_, alt_key="url"
        )
        return img

    def create_video_node(
        self, uri, title=None, name=None, copyright=None, timestamp=None
    ):
        dict_ = {
            "url": uri,
            "title": title,
            "name": name,
            "timestamp": timestamp,
            "copyright": copyright,
        }

        video = self.upsert_node(VideoNode.__name__, dict_, alt_key="url")
        return video

    def create_iframe_node(
        self, uri, description=None, name=None, copyright=None, timestamp=None
    ):
        dict_ = {
            "uri": uri,
            "description": description,
            "name": name,
            "timestamp": timestamp,
            "copyright": copyright,
        }

        video = self.upsert_node(IFrameNode.__name__, dict_, alt_key="uri")
        return video

    def create_author_node(self, author_name, timestamp=None):
        dict_ = {"name": author_name, "timestamp": timestamp}

        author = self.upsert_node(
            GraphCreatorBase._AUTHOR_NODE_NAME, dict_, alt_key="name"
        )

        return author

    def create_web_resource_node(self, url, copyright=None, timestamp=None):
        dict_ = {"url": url, "timestamp": timestamp, "copyright": copyright}

        web_resource = self.upsert_node(
            GraphCreatorBase._WEB_RESOURCE_NODE_NAME, dict_, alt_key="url"
        )
        return web_resource
