from datetime import datetime

from cag.utils.config import Config, configuration

from ..graph.base_graph import *
from pyArango.collection import Document
import re
from typing import Any

from ... import logger

from pyArango.collection import BulkOperation


class Component(object):
    """The class from witch all more specialized components must derive."""

    """
    Structure of the subgraph produced by this component, to be specified in subclass.
    Edge definitions are dictrionaries of the following form:
    {
        'relation': REL_NAME, # Must match a class inheriting from Edge
        'from_collections': COL_NAME, # Must match a class inheriting from Collection
        'to_collections': COL_NAME # Must match a class inheriting from Collection
    }
    """
    _edge_definitions = []
    _base_edge_definitions = []
    _description = "No description"
    _name = "Component"

    def __init__(self, conf: Config = None):
        if conf is None:
            conf = configuration(use_global_conf=True)
        self.conf = conf
        self.database = conf.db
        self.graph_name = conf.graph
        if self.database.hasGraph(self.graph_name):
            self.graph = self.database.graphs[self.graph_name]
        else:
            if not self.database.hasCollection('GenericNode'):
                self.database.createCollection('GenericNode')
            if not self.database.hasCollection('GenericEdge'):
                self.database.createCollection('GenericEdge')
            self.graph: BaseGraph = self.database.createGraph(
                self.graph_name)
        self.arango_db = conf.arango_db

        # Setup graph structure
        for ed in (self._edge_definitions+self._base_edge_definitions):
            self.graph.update_graph_structure(ed['relation'],
                                              ed['from_collections'], ed['to_collections'], create_collections=True)

    def upsert_vert(self, collectionName: str, data: "dict[str, Any]", alt_key: "str | []" = None) -> Document:
        coll: Collection = self.database[collectionName]

        if 'timestamp' not in data.keys() or data['timestamp'] is None:
            data['timestamp'] = datetime.now().isoformat()

        if alt_key is not None:
            if not isinstance(alt_key, list):
                alt_key = [alt_key]
            coll.ensureHashIndex(alt_key, unique=True)
        vert=None
        try:
            vert = self.graph.createVertex(collectionName, data)
        except Exception as e:
            try:
                if alt_key is not None and all(x in data.keys() for x in alt_key):
                    try:
                        query = {k:v for k, v in data.items() if k in alt_key}
                        sample: Document = coll.fetchByExample(
                            query,
                            batchSize=1)[0]
                        if sample is not None:
                            sample.getStore().update(data)
                            sample.save()
                            return sample
                    except Exception as e:
                        logger.exception("An exception was thrown while creating the vertex/edge an alt-key {}"
                                         "with the following data: {} and error: {}".format(collectionName, str(data), e))
                if '_key' in data.keys() and data['_key'] in coll:
                    vert: Document = coll.fetchDocument(data['_key'])
                    for key, d in data.items():
                        vert[key] = d
                    vert.save()
                    return coll[data['_key']]
            except Exception as e:
                logger.exception("An exception was thrown while creating the vertex/edge {}"
                                 "with the following data: {}".format(collectionName, str(data)), e)
        return vert

    def upsert_link(self, relationName: str, from_doc: Document, to_doc: Document, edge_attrs={}, add_id=""):
        
        from_key = re.sub("/", "-", from_doc._id)
        to_key = re.sub("/", "-", to_doc._id)
        add_id = re.sub("/", "-", add_id)
        add_id = f'-{add_id}' if len(add_id) > 0 else ''
        link_key = f'{from_key}-{to_key}{add_id}'
        self.database[relationName].validatePrivate("_from", from_doc._id)
        self.database[relationName].validatePrivate("_to", to_doc._id)

        edge_dic = {'_key': link_key, '_from': from_doc._id,
                    '_to': to_doc._id, **edge_attrs}
        return self.upsert_vert(relationName, edge_dic)
