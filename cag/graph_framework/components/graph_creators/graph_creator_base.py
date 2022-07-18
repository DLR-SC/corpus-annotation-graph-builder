from abc import ABC, abstractmethod

from cag import logger
from pyArango.collection import Document, Collection

from cag.utils.config import Config

from cag.graph_framework.components.component import Component
from datetime import datetime
import re


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

    def __init__(self, corpus_file_or_dir, conf: Config=None):
        super().__init__(conf)
        self.corpus_file_or_dir = corpus_file_or_dir
        self.now = datetime.now()

    @abstractmethod
    def update_graph(self, timestamp):
        g = self.graph

    #########   HELPERS ###########################################################
    def _get_doc_key(self, collection_name, query):
        key = None
        itms = self.database[collection_name].fetchFirstExample(
            query, rawResults=False)
        if len(itms) > 0:
            key = itms[0]['_key']
        return key

    def upsert_vert(self, collectionName, data) -> Document:
        coll: Collection = self.database[collectionName]

        if '_key' in data.keys() and data['_key'] in coll:
            vert: Document = coll.fetchDocument(data['_key'])
            vert.getStore().update(data)
            vert.save()
            return coll[data['_key']]
        else:
            try:
                vert = self.graph.createVertex(collectionName, data)
            except:
                logger.exception("Ane exception was thrown while creating the vertex/edge {}"
                                 "with the following data: {}".format(collectionName, str(data)))
                vert = None
        return vert

    def upsert_link(self, relationName: str, from_doc: Document, to_doc: Document, edge_attrs={}):
        from_key = re.sub("/", "-", from_doc._id)
        to_key = re.sub("/", "-", to_doc._id)
        link_key = f'{from_key}-{to_key}'
        self.database[relationName].validatePrivate("_from", from_doc._id)
        self.database[relationName].validatePrivate("_to", to_doc._id)

        edge_dic = {'_key': link_key, '_from': from_doc._id,
                    '_to': to_doc._id, **edge_attrs}
        return self.upsert_vert(relationName, edge_dic)

    ######### END OF HELPERS ###########################################################

    ######### Generic func to create vertices ##########################################
    def create_corpus_vertex(self, key, name, type, desc, created_on):

        dict_ = {
            "_key": key,
            "name": name,
            "type": type,
            "description": desc,
            "created_on": created_on,
            "timestamp": self.now
        }
        corpus = self.upsert_vert(GraphCreatorBase._CORPUS_NODE_NAME, dict_)
        return corpus

    def create_text_vertex(self, text, timestamp=None):
        if timestamp is None:
            timestamp = self.now
        dict_ = {
            "text": text,
            "timestamp": timestamp
        }
        key = self._get_doc_key(
            GraphCreatorBase._TEXT_NODE_NAME, {"text": text})
        if key is not None:
            dict_["_key"] = key

        txt = self.upsert_vert(
            GraphCreatorBase._TEXT_NODE_NAME, dict_)
        return txt

    def create_image_vertex(self, url):

        dict_ = {
            "url": url,
            "timestamp": self.now
        }

        key = self._get_doc_key(
            GraphCreatorBase._IMAGE_NODE_NAME, {"url": url})
        if key is not None:
            dict_["_key"] = key
        img = self.upsert_vert(
            GraphCreatorBase._IMAGE_NODE_NAME,  dict_)
        return img

    def create_author_vertex(self, author_name, timestamp=None):
        if timestamp is None:
            timestamp = self.now
        dict_ = {
            "name": author_name,
            "timestamp": timestamp
        }

        key = self._get_doc_key(
            GraphCreatorBase._AUTHOR_NODE_NAME, {"name": author_name})

        if key is not None:
            dict_["_key"] = key

        author = self.upsert_vert(
            GraphCreatorBase._AUTHOR_NODE_NAME, dict_)

        return author

    def create_web_resource_vertex(self, url):

        dict_ = {
            "url": url,
            "timestamp": self.now
        }

        key = self._get_doc_key(
            GraphCreatorBase._WEB_RESOURCE_NODE_NAME, {"url": url})

        if key is not None:
            dict_["_key"] = key

        web_resource = self.upsert_vert(
            GraphCreatorBase._WEB_RESOURCE_NODE_NAME, dict_)
        return web_resource
