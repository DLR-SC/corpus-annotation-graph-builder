from pyArango.graph import Graph, EdgeDefinition

import json

from pyArango.theExceptions import CreationError

from cag import logger


class BaseGraph(Graph):
    _edgeDefinitions = [EdgeDefinition('GenericEdge', fromCollections=['GenericNode'], toCollections=['GenericNode'])]
    _orphanedCollections = []

    def _check_and_update_collections(self, collections):
        """Creates new collections from the given collections list if not yet existant."""
        for col in collections:
            if not self.database.hasCollection(col):
                self.database.createCollection(col)

    def update_graph_structure(self, relation, from_collections, to_collections, create_collections=True, waitForSync = False):
        """
        Adds an edge definition to the graph if it not already exists. Otherwhise the existing edge definition becomes updated if necessary based on the given collections.
        In case of an update, this method never deletes collections from an edge definition but creates a union of the existing and provided collections.

        Parameters:
            relation (required string): Name of the edge collection defining the relation.
            from_collections (required [string]): List of names of node collections appearing as origin of edges.
            to_collections (required [string]): List of names of node collections appearing as destination of edges.
            create_collections (optional boolean, default: true): If true collections will be created if they not exist.
            waitForSync (optional boolean, default: False): See ArangoDBs doc for possible col arguments.
        Returns:
            Boolean value indicating if the edge definitions of this graph have been updated.
        """
        is_new_relation = True
        if relation in self.definitions.keys():
            is_new_relation = False

            existings_froms = set(self.definitions[relation].fromCollections)
            existing_tos = set(self.definitions[relation].toCollections)

            proposed_froms = set(from_collections)
            proposed_tos = set(to_collections)

            new_froms = proposed_froms - existings_froms
            new_tos = proposed_tos - existing_tos

            if create_collections and len(new_froms) > 0:
                self._check_and_update_collections(new_froms)


            if create_collections and (len(new_tos) > 0):
                self._check_and_update_collections(new_tos)

            if (len(new_froms ) > 0) or (len(new_tos) > 0):
                 url = '%s/edge/%s' % (self.getURL(), relation)
                 from_collections = list(existings_froms | new_froms)
                 to_collections = list(existing_tos | new_tos)
            else:
                logger.debug(f"edge  found {relation} but has no changes")
                return False

            logger.debug(f"edge  found {relation}, updating it")
            r = self.connection.session.put(url, data=json.dumps(
                {
                    'collection': relation,
                    'from': from_collections,
                    'to': to_collections
                }, default=str), params={'waitForSync': waitForSync}
                                            )
        else:
            logger.debug(f"edge not found {relation}, adding it")
            url = '%s/edge' % self.getURL()
            r = self.connection.session.post(url, data=json.dumps(
                {
                    'collection': relation,
                    'from': from_collections,
                    'to': to_collections
                },
                default=str), params={'waitForSync': waitForSync}
                                             )



        data = r.json()
        if r.status_code == 201 or r.status_code == 202:
            self.definitions[relation] = EdgeDefinition(relation, fromCollections = from_collections, toCollections = to_collections)
            return True

        raise CreationError("Unable to modify edge definitions., %s" % data["errorMessage"], data)