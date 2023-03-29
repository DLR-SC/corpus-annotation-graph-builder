from datetime import datetime

from pyArango.theExceptions import DocumentNotFoundError, SimpleQueryError

from cag.graph_elements.nodes import GenericOOSNode
from cag.graph_elements.relations import GenericEdge
from cag.utils.config import Config, configuration

from cag.graph_elements.base_graph import *
from pyArango.collection import Document, Collection, Collection_metaclass
import re
from typing import Any, Optional, Union
from tenacity import retry
from tenacity.stop import stop_after_delay
from tenacity.retry import retry_if_not_exception_type
from tenacity.wait import wait_random
from cag import logger


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
        edges = self._base_edge_definitions + self._edge_definitions

        if conf is None:
            conf = configuration(use_global_conf=True)
        self.conf = conf
        self.database = conf.db
        self.graph_name = conf.graph
        if self.database.hasGraph(self.graph_name):
            self.graph: BaseGraph = self.database.graphs[self.graph_name]
        else:
            edge_def_arr = []
            for ed in edges:
                for col in (
                    [ed["relation"]]
                    + ed["from_collections"]
                    + ed["to_collections"]
                ):

                    if not self.database.hasCollection(
                        self.get_collection_name(col)
                    ):
                        self.database.createCollection(
                            self.get_collection_name(col)
                        )
                edge_def_arr.append(
                    EdgeDefinition(
                        self.get_collection_name(ed["relation"]),
                        fromCollections=[
                            self.get_collection_name(col)
                            for col in ed["from_collections"]
                        ],
                        toCollections=[
                            self.get_collection_name(col)
                            for col in ed["to_collections"]
                        ],
                    )
                )
            if len(edge_def_arr) == 0:
                raise CreationError(
                    "You have to define an edge for your graph in the your graph creator"
                )
            _ = type(
                self.graph_name,
                (BaseGraph,),
                {"_edgeDefinitions": edge_def_arr},
            )
            self.graph: BaseGraph = self.database.createGraph(self.graph_name)

        self.graph.__class__ = BaseGraph
        self.arango_db = conf.arango_db

        # Setup graph structure
        for ed in edges:
            self.graph.update_graph_structure(
                self.get_collection_name(ed["relation"]),
                [
                    self.get_collection_name(col)
                    for col in ed["from_collections"]
                ],
                [
                    self.get_collection_name(col)
                    for col in ed["to_collections"]
                ],
                create_collections=True,
            )

    @staticmethod
    def get_collection_name(
            collection: Union[str, Collection_metaclass]
    ) -> str:
        """
        Returns the name of a collection based on the input collection. If the collection is a string,
        it returns the same string. If the collection is an instance of Collection_metaclass, it tries
        to return the '_name' attribute of the class. If '_name' is not available, it returns the class
        name. Raises ValueError if the input collection is not a string or an instance of
        Collection_metaclass.

        Args:
            collection (Union[str, Collection_metaclass]): The input collection, which can be a string
                or an instance of Collection_metaclass.

        Returns:
            str: The name of the collection.

        Raises:
            ValueError: If the input collection is not a string or an instance of Collection_metaclass.
        """
        if isinstance(collection, str):
            # Backward compatibility, when strings are used in edge definition
            return collection
        if isinstance(collection, Collection_metaclass):
            # When a class of GenericOOSNode gets passed, we take the _name if possible
            if hasattr(collection, "_name"):
                return collection._name  # noqa
            else:
                # Otherwise just take the name of the class
                return collection.__name__
        raise ValueError(
            f"{collection} is of incompatible type {type(collection)}"
            f"Make sure it's a str, GenericOOSNode or GenericEdge!"
        )

    @retry(wait=wait_random(min=1, max=3), stop=stop_after_delay(180))
    def get_document(
        self,
        collectionName: str,
        data: "dict[str, Any]",
        alt_key: "str | []" = None,
    ) -> "Optional[Document]":
        """Gets the node if it exists.
        In case alt_key is provided, it queries the node based on the alt_key keys and values in the data dict.
        In case alt_key is not provided and _key is part of the data dict, it fetches the document based on it.
        Otherwise it returns None

        :param collectionName: On which collection to search on
        :type collectionName: str
        :param data: the dict where the keys should be present
        :type data: dict[str, Any]
        :param alt_key: an alternate key to search on, defaults to None
        :type alt_key: str|list[str], optional
        :return: the found document, if not exists: None
        :rtype: Document, optional
        """
        """

        """
        coll: Collection = self.database[collectionName]
        node = None
        try:
            if type(alt_key) == str:
                alt_key = [alt_key]

            if (
                alt_key is None
                and "_key" in data.keys()
                and data["_key"] in coll
            ):
                node: Document = coll.fetchDocument(data["_key"])
            elif alt_key is not None and all(
                x in data.keys() for x in alt_key
            ):
                coll.ensureHashIndex(alt_key, unique=True)

                query = {k: v for k, v in data.items() if k in alt_key}

                resp = coll.fetchByExample(query, batchSize=1)
                if len(resp) > 0:
                    node: Document = resp[0]
            else:
                logger.debug(
                    "node does not exist - make sure you provide _key as part of data dict "
                    "or alt_key as a lst and part of the data dict"
                )
        except (DocumentNotFoundError, SimpleQueryError) as e:
            logger.debug(
                "Document was not found for data {} and node {} - message: {}".format(
                    collectionName, str(data), e.message
                )
            )
        except Exception as unknown_e:
            logger.error(
                "get_document - An unknown error was thrown for data {} and node {} - message: {}".format(
                    collectionName, str(data), str(unknown_e)
                )
            )
            raise Exception("raising get_document")
        return node

    @retry(wait=wait_random(min=1, max=3), stop=stop_after_delay(180))
    def upsert_node(
        self,
        collectionName: str,
        data: "dict[str, Any]",
        alt_key: "str | []" = None,
    ) -> Document:
        """Upsert an item in a collection based on a _key or any other property

        :param collectionName: the collection to work on
        :type collectionName: str
        :param data: a dictionary with your data
        :type data: dict[str, Any]
        :param alt_key: on which key the upsert should look for existing data (if there are multiple,
        the first match will return and it combines all key into a fetch-by-example-query), defaults to None
        :type alt_key: str | [], optional
        :return: the upserted Document
        :rtype: Document
        """
        coll: Collection = self.database[collectionName]

        if "timestamp" not in data.keys() or data["timestamp"] is None:
            data["timestamp"] = datetime.now().isoformat()

        node = None
        try:
            node: Document = self.get_document(collectionName, data, alt_key)
            if node is None:
                node = self.graph.createVertex(collectionName, data)
            else:
                logger.debug("updating existing node")
                for key, d in data.items():
                    node[key] = d
                node.save()
                node = coll[node._key]
            if node is None:
                raise Exception('the node is None')
        except Exception as e:
            logger.info(
                f"UPSERT_NODE - An unknown exception of type {str(type(e))} was thrown for "
                f"data {collectionName} and node {str(data)} -"
                f" message: {str(e)}"
            )
            raise Exception(f"UPSERT_NODE {str(e)}")

        return node

    @retry(wait=wait_random(min=1, max=3), stop=stop_after_delay(180))
    def get_edge_attributes(
        self,
        relationName: str,
        from_doc: Document,
        to_doc: Document,
        edge_attrs={},
        add_id="",
    ):
        """Gets a edge

        :param relationName: which edge collection to create this edge on
        :type relationName: str
        :param from_doc: the document where this relation starts
        :type from_doc: Document
        :param to_doc: the document where this relation leads to
        :type to_doc: Document
        :param edge_attrs: attributes to add to edge (provenance), defaults to {}
        :type edge_attrs: dict, optional
        :param add_id: data to append the id (if the from-to relation may not be unique), defaults to ""
        :type add_id: str, optional
        :return: the  edge document if it exists
        :rtype: 'Dict[str|Any]'
        """
        from_key = re.sub("/", "-", from_doc._id)
        to_key = re.sub("/", "-", to_doc._id)
        add_id = re.sub("/", "-", add_id)
        add_id = f"-{add_id}" if len(add_id) > 0 else ""
        edge_key = f"{from_key}-{to_key}{add_id}"
        try:
            self.database[relationName].validatePrivate("_from", from_doc._id)
            self.database[relationName].validatePrivate("_to", to_doc._id)

        except Exception as e:
            raise Exception(f"get_edge_attributes {str(e)}")

        edge_dic = {
            "_key": edge_key,
            "_from": from_doc._id,
            "_to": to_doc._id,
            **edge_attrs,
        }
        return edge_dic

    @retry(wait=wait_random(min=1, max=3), stop=stop_after_delay(180)), retry=retry_if_not_exception_type(ValueError))
    def upsert_edge(
        self,
        relationName: str,
        from_doc: Document,
        to_doc: Document,
        edge_attrs={},
        add_id="",
    ):
        """Upsert a edge (will generate a synthetic key from the provided documents, can optionally add something to these keys and edges)

        :param relationName: which edge collection to create this edge on
        :type relationName: str
        :param from_doc: the document where this relation starts
        :type from_doc: Document
        :param to_doc: the document where this relation leads to
        :type to_doc: Document
        :param edge_attrs: attributes to add to edge (provenance), defaults to {}
        :type edge_attrs: dict, optional
        :param add_id: data to append the id (if the from-to relation may not be unique), defaults to ""
        :type add_id: str, optional
        :return: the upserted edge document
        :rtype: Document
        """
        if from_doc is None or to_doc is None:
            raise ValueError('upsert_edge - from or to has a None Value')

        data = self.get_edge_attributes(
            relationName, from_doc, to_doc, edge_attrs, add_id
        )

        coll: Collection = self.database[relationName]

        if "timestamp" not in data.keys() or data["timestamp"] is None:
            data["timestamp"] = datetime.now().isoformat()

        edge = None
        try:
            edge: Document = self.get_document(relationName, data)
            if edge is None:
                edge = self.graph.createEdge(
                    relationName, from_doc._id, to_doc._id, data
                )
            else:
                logger.debug("updating existing node")
                for key, d in data.items():
                    edge[key] = d
                edge.save()
                edge = coll[edge._key]
            if edge is None:
                raise Exception('the edge is None')
        except Exception as e:
            logger.info(
                f"UPSERT_EDGE - An unknown exception of type {str(type(e))} was thrown for "
                f"data {relationName} and node {str(data)} -"
                f" message: {str(e)}"
            )
            raise Exception(f"get_edge_attributes {str(e)}")

        return edge
