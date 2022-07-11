from datetime import datetime

from ..utils.config import Config, configuration

from ..graph.nodes import *
from ..graph.relations import *
from ..graph.base_graph import *
from pyArango.database import Database
from pyArango.graph import Graph
from pyArango.collection import Document
import re
from typing import Any

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
    # TODO: make graph name configurable

    def __init__(self, conf: Config = None):
        if conf is None:
            conf = configuration(use_global_conf=True)
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

        # Setup graph structure
        for ed in (self._edge_definitions+self._base_edge_definitions):
            self.graph.update_graph_structure(ed['relation'],
                                              ed['from_collections'], ed['to_collections'], create_collections=True)

    def upsert_vert(self, collectionName: str, data: "dict[str, Any]") -> Document:
        coll: Collection = self.database[collectionName]
        data['timestamp'] = datetime.now().isoformat()
        if data['_key'] in coll:
            vert: Document = coll.fetchDocument(data['_key'])
            for key, d in data.items():
                vert[key] = d
            vert.save()
            return coll[data['_key']]
        else:
            vert = self.graph.createVertex(collectionName, data)
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
