import os
import math
from cag.utils.config import Config
from cag.utils import utils
from cag.framework.component import Component
from cag import logger
from dataclasses import dataclass
from operator_enum import OperatorEnum
from objects.GraphFlow import GraphFlow
from aql_queries import (
    UNION_START_NODES,
    GET_DOCUMENTS_FILTERS_USING_COLLECTION,
    GET_DOCUMENTS_FILTERS_USING_VIEW,
    GET_GRAPH,
)

DB_LABEL_ATTRIBUTE = "DB_LABEL_ATTRIBUTE"
SYSTEM_PROPS = ["_key", "_id", "_rev", "_from", "_to"]
FROM_VERTEX_COLLECTIONS = "from_vertex_collections"
TO_VERTEX_COLLECTIONS = "to_vertex_collections"
COLLECTION = "collection"
ATTRIBUTE = "attribute"
ATTRIBUTE_TYPE = "attributeType"
OPERATOR = "operator"
VALUE = "value"
LOOP_VAR = "doc"
P = "p"
START_NODES_VAR = "start_nodes"
VERTEX_COLLECTIONS = "vertex_collections"
EDGE_COLLECTIONS = "edge_collections"
MIN = "min"
MAX = "max"
BASE_DIRECTION = "base_direction"
INBOUND = "INBOUND"
OUTBOUND = "OUTBOUND"
ANY = "ANY"
NUMBER_OF_START_NODES = 1000

@dataclass
class UserData:
    attribute: str
    attributeType: str
    operator: OperatorEnum
    value: str

@dataclass
class NodeDTO:
    id: str
    collection: str
    userData: list[UserData]

@dataclass
class EdgeDTO:
    id: str
    source: str
    target: str
    name: str
    userData: list[UserData]

@dataclass
class GraphData:
    nodes: list[NodeDTO]
    edges: list[EdgeDTO]


# TODO Put this into utils.py
def generate_random_string(length:int) -> str:
    import string
    import random
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str


class QueryBuilder(Component):

    def __init__(self, config: Config) -> None:

        super().__init__(config)

        print("Works: ", self.database)
        # print("Works not: ", self.test)
        
        self.edge_definitions = self.arango_db.graph(config.graph).edge_definitions()
        self.vertex_collections = self.arango_db.graph(config.graph).vertex_collections()

        # self.flow will eventually contain the graph that is to be queried
        self.flow:GraphFlow = None

    def _map_operator(self, operator: str):
        """
        Maps certain operator names to the internal representation.

        Args:
            operator (str): Operator name

        Returns:
            str: The operators' internal representation
        """
        
        mapping = {
            'equals': 'equals',
            'equals_not': 'equalsNot',
            'alphabetic_contains': 'contains',
            'alphabetic_contains_not': 'containsNot',
            'alphabetic_starts_with': 'startsWith',
            'alphabetic_ends_with': 'endsWith',
            'numeric_equals': '=',
            'numeric_smaller_than': '<',
            'numeric_smaller_or_equal': '<=',
            'numeric_larger_than': '>',
            'numeric_larger_or_equal': '>=',
            'date_smaller_than': 'before',
            'date_smaller_or_equal': 'onOrBefore',
            'date_larger_than': 'after',
            'date_larger_or_equal': 'onOrAfter',
        }
        return mapping[operator]

    def _build_aql_condition(self,
                            field: str,
                            operator: str,
                            value: str,
                            datatype: str,
                            loop_var: str,
                            bind_vars: dict,
                            prepend_filter_clause=False,
                            uses_view=False
                            ):
        """
        Builds the >>conditional<< part of an AQL 'FILTER' statement.
        E.g.:          'CONTAINS(a.name, "bob")'
        Not:    'FILTER CONTAINS(a.name, "bob")'

        Args:
            field (str): The field to use (e.g. 'name' in 'a.name == "Bob")
            operator (str): The internal name of the operator to apply (e.g. 'contains' for 'CONTAINS(a.name, "bob"))'
            value (str): The value to use
            datatype (str): The datatype of the value
            loop_var (str): The name of the current variable for the loop (e.g. 'doc' in 'FOR doc IN documents FILTER doc.name == "Bob"')
            bind_vars (dict): Bind parameters for AQL query
            prepend_filter_clause (bool): Whether or not to prepend a FILTER (or SEARCH) clause
            uses_view (bool): Whether or not to apply a view (uses different operator names)

        Returns:
            str: The constructed conditional statement
        """

        if not value or not datatype:
            filter_statement = "true"
        else:
            # Prepare a randomly named bind parameter. Random in order to avoid name collisions when this function is called multiple times for the same query
            bind_field = f"field_{generate_random_string(10)}"
            bind_value = f"value_{generate_random_string(10)}"

            # Case: Text
            if datatype == "text":
                if uses_view:
                    operator_map = {
                        'contains': f'PHRASE({loop_var}.@{bind_field}, @{bind_value}, "text_en") /* "{field}" contains "{value}" */',
                        'containsNot': f'{loop_var}.@{bind_field} NOT IN TOKENS(@{bind_value}) /* "{field}" does not "{value}" */',
                        'equals': f'{loop_var}.@{bind_field} == @{bind_value} /* "{field}" equals "{value}" */',
                        'equalsNot': f'{loop_var}.@{bind_field} != @{bind_value} /* "{field}" does not equal "{value}" */',
                        'startsWith': f'STARTS_WITH({loop_var}.@{bind_field}, @{bind_value}) /* "{field}" starts with "{value}" */',
                        # 'endsWith': f'STARTS_WITH(REVERSE({loop_var}.@{bind_field}), REVERSE(@{bind_value}))'
                    }
                else:
                    operator_map = {
                        'contains': f'CONTAINS(LOWER({loop_var}.@{bind_field}), LOWER(@{bind_value})) /* "{field}" contains "{value}" */',
                        'containsNot': f'NOT CONTAINS(LOWER({loop_var}.@{bind_field}), LOWER(@{bind_value})) /* "{field}" does not "{value}" */',
                        'equals': f'LOWER({loop_var}.@{bind_field}) == LOWER(@{bind_value}) /* "{field}" equals "{value}" */',
                        'equalsNot': f'LOWER({loop_var}.@{bind_field}) != LOWER(@{bind_value}) /* "{field}" does not equal "{value}" */',
                        'startsWith': f'STARTS_WITH({loop_var}.@{bind_field}, @{bind_value}) /* "{field}" starts with "{value}" */',
                        # 'endsWith': f'STARTS_WITH(REVERSE({loop_var}.@{bind_field}), REVERSE(@{bind_value}))'
                    }

            # Case: Number
            elif datatype == "number":
                if uses_view:
                    operator_map = {
                        '=': f'{loop_var}.@{bind_field} == @{bind_value} /* "{field}" equals "{value}" */',
                        '!=': f'{loop_var}.@{bind_field} != @{bind_value} /* "{field}" does not equal "{value}" */',
                        '<': f'{loop_var}.@{bind_field} < @{bind_value} /* "{field}" smaller than "{value}" */',
                        '>': f'{loop_var}.@{bind_field} > @{bind_value} /* "{field}" larger than "{value}" */',
                        '<=': f'{loop_var}.@{bind_field} <= @{bind_value} /* "{field}" smaller or equal "{value}" */',
                        '>=': f'{loop_var}.@{bind_field} >= @{bind_value} /* "{field}" larger or equal "{value}" */',
                    }
                else:
                    operator_map = {
                        '=': f'{loop_var}.@{bind_field} == @{bind_value} /* "{field}" equals "{value}" */',
                        '!=': f'{loop_var}.@{bind_field} != @{bind_value} /* "{field}" does not equal "{value}" */',
                        '<': f'{loop_var}.@{bind_field} < @{bind_value} /* "{field}" smaller than "{value}" */',
                        '>': f'{loop_var}.@{bind_field} > @{bind_value} /* "{field}" larger "{value}" */',
                        '<=': f'{loop_var}.@{bind_field} <= @{bind_value} /* "{field}" smaller or equal "{value}" */',
                        '>=': f'{loop_var}.@{bind_field} >= @{bind_value} /* "{field}" larger or equal "{value}" */',
                    }

            # Case: Date
            elif datatype in ["date", "datetime"]:
                operator_map = {
                    'equals': f'{loop_var}.@{bind_field} == DATE_ISO8601(@{bind_value}) /* "{field}" equals "{value}" */',
                    'is': f'{loop_var}.@{bind_field} == DATE_ISO8601(@{bind_value}) /* "{field}" equals "{value}" */',
                    'isNot': f'{loop_var}.@{bind_field} != DATE_ISO8601(@{bind_value}) /* "{field}" does not equal "{value}" */',
                    'after': f'{loop_var}.@{bind_field} > DATE_ISO8601(@{bind_value}) /* "{field}" after "{value}" */',
                    'before': f'{loop_var}.@{bind_field} < DATE_ISO8601(@{bind_value}) /* "{field}" before "{value}" */',
                    'onOrAfter': f'{loop_var}.@{bind_field} >= DATE_ISO8601(@{bind_value}) /* "{field}" on or after "{value}" */',
                    'onOrBefore': f'{loop_var}.@{bind_field} <= DATE_ISO8601(@{bind_value}) /* "{field}" on or before "{value}" */',
                }

            # Add bind variables for the query (the field names and their value)
            bind_vars[bind_field] = field
            bind_vars[bind_value] = value

            # Sometimes, due to the frontend, the same operator moght have different names. Normalize the names here.
            if operator not in operator_map:
                operator = self._map_operator(operator)
            filter_statement = operator_map[operator]

        # If necessary, prepend a "SEARCH" or "FILTER" clause to the statement
        if prepend_filter_clause:
            if uses_view:
                filter_statement = f'SEARCH {filter_statement}'
            else:
                filter_statement = f'FILTER {filter_statement}'
        return filter_statement, bind_vars

    def _validate_graph_data(self, graph_data:GraphData) -> None:
        """
        Ensures that the provided graph data has the correct format.
        Only performs a shallow check:
        1.) checks whether 'nodes' and 'edges' are defined
        2.) checks whether 'nodes' and 'edges' are of type 'list'
        3.) checks whether 'nodes' is not empty

        4.) checks whether all nodes have the required properties
        5.) checks datatypes of top-level attributes of each node
        6.) checks whether all node collections are actually contained in the database
        7.) checks whether userData of nodes contains the necessary attributes

        8.) checks whether all edges have the required properties
        9.) checks datatypes of top-level attributes of each edge
        10.) checks whether all edge collections are actually contained in the database
        11.) checks whether userData of edges contains the necessary attributes

        Args:
            graph_data (GraphData): The graph data to validate

        Raises:
            AssertionError: If graph_data is of an invalid format
        """

        # 1.)
        assert 'nodes' in graph_data, "Graph data does not contain a node list labeled `nodes`."
        assert 'edges' in graph_data, "Graph data does not contain an edge list labeled `edges`."

        # 2.)
        assert isinstance(graph_data.get('nodes'), list), "Node list in graph data is not of type list."
        assert isinstance(graph_data.get('edges'), list), "Edge list in graph data is not of type list."

        # 3.)
        assert graph_data.get('nodes'), "Node list in graph data is empty."

        for node in graph_data.get('nodes'):
            # 4.) & 5.)
            assert 'id' in node, "At least one node in 'nodes' of graph_data does not contain an 'id' property."
            assert isinstance(node.get('id'), str), f'"id" of node with id "{node.get("id")}" must be a string.'
            assert 'collection' in node, "At least one node in 'nodes' of graph_data does not contain a 'collection' property."
            assert isinstance(node.get('collection'), str), f'"collection" of node with id "{node.get("id")}" must be a string.'
            assert 'userData' in node, "At least one node in 'nodes' of graph_data does not contain a 'userData' property."
            assert isinstance(node.get('userData'), list), f'"userData" of node with id "{node.get("id")}" must be a list.'
            
            # 6.)
            assert node.get('collection') in self.vertex_collections, f'Node with id "{node.get("id")}" has an invalid collection name: "{node.get("collection")}"'

            # 7.)
            for ud in node.get('userData'):
                assert 'attribute' in ud, f'An element within "userData" of node with id "{node.get("id")}" is missing a property "attribute"'
                assert 'attributeType' in ud, f'An element within "userData" of node with id "{node.get("id")}" is missing a property "attributeType"'
                assert 'operator' in ud, f'An element within "userData" of node with id "{node.get("id")}" is missing a property "text"'
                assert 'value' in ud, f'An element within "userData" of node with id "{node.get("id")}" is missing a property "value"'
        
        for edge in graph_data.get('edges'):
            # 8.) & 9.)
            assert 'id' in edge, "At least one edge in 'edges' of graph_data does not contain an 'id' property."
            assert isinstance(edge.get('id'), str), f'"id" of edge with id "{edge.get("id")}" must be a string.'
            assert 'name' in edge, "At least one edge in 'edges' of graph_data does not contain a 'name' property."
            assert isinstance(edge.get('name'), str), f'"name" of edge with id "{edge.get("id")}" must be a string.'
            assert 'source' in edge, "At least one edge in 'edges' of graph_data does not contain a 'source' property."
            assert isinstance(edge.get('source'), str), f'"source" of edge with id "{edge.get("id")}" must be a string.'
            assert 'target' in edge, "At least one edge in 'edges' of graph_data does not contain a 'target' property."
            assert isinstance(edge.get('target'), str), f'"target" of edge with id "{edge.get("id")}" must be a string.'
            assert 'userData' in edge, "At least one edge in 'edges' of graph_data does not contain a 'userData' property."
            assert isinstance(edge.get('userData'), list), f'"userData" of edge with id "{edge.get("id")}" must be a list.'
            
            # 10.)
            assert any(coll_def.get('edge_collection') == edge.get('name') for coll_def in self.edge_definitions), f'Edge with id "{edge.get("id")}" has an invalid collection name: "{edge.get("name")}"'

            # 11.)
            for ud in edge.get('userData'):
                assert 'attribute' in ud, f'An element within "userData" of edge with id "{edge.get("id")}" is missing a property "attribute"'
                assert 'attributeType' in ud, f'An element within "userData" of edge with id "{edge.get("id")}" is missing a property "attributeType"'
                assert 'operator' in ud, f'An element within "userData" of edge with id "{edge.get("id")}" is missing a property "text"'
                assert 'value' in ud, f'An element within "userData" of edge with id "{edge.get("id")}" is missing a property "value"'
            

    def _has_view(self, collection_name) -> bool:
        # TODO
        return False
    
    def _get_view(self, collection_name) -> bool:
        # TOOD
        return None
    
    def _build_node_filter(self, index: str, nodes: list, bind_vars: dict, p:str) -> tuple[list, dict]:
        """
        This function generates AQL conditional statements for each node passed to the function.
        A node can have multiple conditions, leading to multiple conditional statements.
        A conditional statement could, for example, look like this: 
        'p.vertices[1].age > 10'
        Note that this function does not include AQL statements like "FILTER" or "SEARCH".

        Arguments:
            index (list): Index refers to the index of the node in the path, for which the conditional state should be generated.
            nodes (list): List of nodes for which conditional statements should be generated.
            bind_vars (dict): Bind parameters for the AQL query
            p (str): The variable used to reference a "path" in the AQL query (e.g. as in "p.vertices"). Typically the character 'p'

        Returns:
            (list, dict): The conditional statements for the nodes and the updated bind parameter dictionary.        
        """

        # Create the conditions for each node
        node_filters = list()
        loop_var = "{p}.vertices[{index}]".format(p=p, index=index)
        for node in nodes:
            # Create condition statement to match the nodes' collection (e.g. IS_SAME_COLLECTION(p.vertices[1], "TextNode"))
            bind_var_name = generate_random_string(10)
            bind_vars[bind_var_name] = node.collection
            cond_collection = f'(IS_SAME_COLLECTION({loop_var}, @{bind_var_name})) /* Vertex at index {index} is of "{bind_vars[bind_var_name]}" collection */ '
            node_filters.append(cond_collection)

            # Create condition statement for each nodes property/condition
            for condition in node.conditions:
                attribute = condition[ATTRIBUTE]
                attributeType = condition[ATTRIBUTE_TYPE]
                #operator = condition[OPERATOR][VALUE]
                operator = condition[OPERATOR]
                value = condition[VALUE]

                # 2. Create condition for property (e.g. p.vertices[index].name == "Peter")
                cond_property, bind_vars = self._build_aql_condition(
                    field=attribute,
                    operator=operator,
                    value=value,
                    datatype=attributeType,
                    loop_var=loop_var,
                    bind_vars=bind_vars
                )

                # Add brackets around the conditional statement
                cond_property = f"({cond_property})"
                node_filters.append(cond_property)
        return node_filters, bind_vars

    def _build_edge_filter(self, index: str, edges: list, bind_vars: dict, p:str) -> tuple[list, dict]:
        """
        This function generates AQL conditional statements for each edge passed to the function.
        An edge can have multiple conditions, leading to multiple conditional statements.
        A conditional statement could, for example, look like this: 
        'p.edge[0].size < 100'
        Note that this function does not include AQL statements like "FILTER" or "SEARCH".

        Arguments:
        - index: list
            Index refers to the index of the edge in the path, for which the conditional state should be generated.
        - edges: list
            List of edges for which conditional statements should be generated.
        - bind_vars: dict
            Bind parameters for the AQL query
        - p: str
            The variable used to reference a "path" in the AQL query (e.g. as in "p.vertices"). Typically the character 'p'
        """

        # Create conditions for each edge
        edge_filters = list()
        loop_var = "{p}.edges[{index}]".format(p=p, index=index-1)
        for edge in edges:
            if not edge.conditions:
                continue

            # Create conditional statement for each property/condition of the edge
            for condition in edge.conditions:
                value = condition[VALUE]
                if not value:
                    continue

                # Create EdgeProperty instance for easier data handling
                attribute = condition[ATTRIBUTE]
                attribute_type = condition[ATTRIBUTE_TYPE]
                # operator = condition[OPERATOR][VALUE]
                operator = condition[OPERATOR]

                # Create condition for property (e.g. p.edges[0]._key == 50)
                cond_property, bind_vars = self._build_aql_condition(field=attribute,
                                                                    operator=operator,
                                                                    value=value,
                                                                    datatype=attribute_type,
                                                                    loop_var=loop_var,
                                                                    bind_vars=bind_vars)
                edge_filter = f"({cond_property})"
                edge_filters.append(edge_filter)
        return edge_filters, bind_vars
    
    def _build_aql_path_filter(self, path:list, bind_vars:dict) -> tuple[str, dict]:
        """
        This function creates a conditional statement for an AQL query, where each statement
        filters a complete path. `path` is a list of tuples, where the first item of each tuple is an Edge
        and the second item in each tuple is a Node: [(edge, node), (edge, node), ...]

        E.g.: a single conditional statement for a full path could look like this:
        '
            (
                IS_SAME_COLLECTION(p.vertices[0], "Document")
                AND
                p.vertices[1].name == "Bob
            )
        '
        """

        filters = list()
        filter_statement = ''
        # 1.: Iterate each element (i.e. each edge-node pair) in the path
        for index, (edge, node) in enumerate(path):
            # 2.: Create all conditional clauses for the edge and store them in a list
            if edge:
                edge_filters, bind_vars = self._build_edge_filter(
                    index=index,
                    edges=[edge],
                    bind_vars=bind_vars,
                    p=P
                )
                filters.extend(edge_filters)

            # 3.: Create all conditional clauses for the node and store them in the same list
            node_filters, bind_vars = self._build_node_filter(
                index=index,
                nodes=[node],
                bind_vars=bind_vars,
                p=P
            )
            filters.extend(node_filters)

            # 4.: Combine all conditional statements and combine them in a string using AND
            joined_filters = ' AND '.join(filters)

            # 5.: Surround statement by round brackets
            filter_statement = f'({joined_filters})'
        return filter_statement, bind_vars
    
    def _build_query_start_nodes(self,
                                source_nodes:list,
                                max_start_nodes:int,
                                bind_vars:dict) -> tuple[str, dict]:
        """
        This function generates parts of an AQL query that is used to obtain all source nodes from
        the database.
        A sample could look like this:
        '
            LET q1 = FOR doc IN Documents RETURN doc
            LET start_nodes = UNION(q1, [])
        '
        The query part is not executable by itself as it is meant to be used as part of a 
        larger AQL query later on.

        Args:
            source_nodes (list): List of source nodes. All of them must be obtained through the AQL query.
            max_start_nodes (int): Maximum number of total start nodes to obtain. Sets a corresponding LIMIT in the AQL clause.
            bind_vars (dict): Running bind parameters for the AQL query.

        Returns:
            (str, dict): AQL query and running bind parameters
        """
        
        # This will hold the final query for the start nodes
        start_node_query = ''

        # This will hold the names for each sub-query (e.g. "q1" in "LET q1 = FOR doc IN Documents ...")
        query_identifiers = list()

        # Based on the total number of documents to obtain (`max_start_nodes`), calculate how many docs should be drawn from each distinct collection
        source_nodes_count = len(source_nodes)
        docs_per_collection = math.floor(max_start_nodes/source_nodes_count)

        # For each source node (i.e. each collection), create a sub-query
        for i, source_node in enumerate(source_nodes):
            filters = list() # List of filters will contain all conditions for the current node
            query_id = f'{LOOP_VAR}_{i}' # Variable to identify each sub query of the AQL
            collection = source_node.collection
            has_view = self._has_view(collection)
            view_name = self._get_view(collection)

            # Iterate all node conditions in order to create the according node filters ("FILTER" statements)
            for condition in source_node.conditions:
                filter_aql, bind_vars = self._build_aql_condition(
                    field=condition[ATTRIBUTE],
                    operator=condition[OPERATOR],
                    value=condition[VALUE],
                    datatype=condition[ATTRIBUTE_TYPE],
                    loop_var=LOOP_VAR,
                    bind_vars=bind_vars,
                    prepend_filter_clause=(not has_view),
                    uses_view=has_view
                )
                filters.append(filter_aql)

            # If a view exists for the collection type, then use views to query the start nodes
            if has_view:
                filters = 'SEARCH ' + '\nAND\n '.join(filters) if filters else ''
                aql_start_nodes = GET_DOCUMENTS_FILTERS_USING_VIEW.format(
                    query_var=query_id,
                    loop_var=LOOP_VAR,
                    view=view_name,
                    filters=filters,
                    limit=f'LIMIT {max_start_nodes}' if max_start_nodes and max_start_nodes > 0 else f'LIMIT {docs_per_collection}'
                )

            # If no view exists for the collection type, then iterate the collection normally without using views
            else:
                filters = ' '.join(filters)
                aql_start_nodes = GET_DOCUMENTS_FILTERS_USING_COLLECTION.format(
                    query_var=query_id,
                    loop_var=LOOP_VAR,
                    collection=collection,
                    filters=filters,
                    limit=f'LIMIT {max_start_nodes}' if max_start_nodes and max_start_nodes > 0 else f'LIMIT {docs_per_collection}'
                )

            # Append current query to the query that gets all start nodes
            start_node_query = start_node_query + ' \n' + aql_start_nodes

            # Save the loop var for later
            query_identifiers.append(query_id)

        
        # Create merged query. If start nodes come from multiple collections, they are obtain in a separate query each (above) and put in a list.
        # Below code now creates the AQL query to place all documents into a single list.
        # E.g.:
        # Above code produces:
        # 'LET q1 = FOR d IN Person RETURN p
        #  LET q2 = FOR b IN Building RETURN b'
        #
        # Then below code adds:
        # 'LET start_nodes = UNION(q1, q2, [])'
        #
        # The empty bracket is placed in case there is only one q1 as in that case, UNION would fail due to insufficient number of arguments.
        aql_union_start_nodes = UNION_START_NODES.format(
            var=START_NODES_VAR,
            lists=', '.join(query_identifiers)
        )

        start_node_query = start_node_query + ' \n' + aql_union_start_nodes

        # Return result
        return start_node_query, bind_vars
    
    def _edge_direction(self, collection_a: str, collection_b: str, use_graph_definition: bool = False):
        """
        Checks the direction of the edge between the two collections in the graph definition.
        If an edge exists between the two given collections, this function returns its
        direction. If `use_graph_definition` is True, the direction is checked based of the
        actual graph definition rather than the manually provided and custom meta edges.
        Returns:
            -1, if collection_a is the target node and collection_b is the source node (i.e. inbound edge)
            0, if the edge does not exists between the two given nodes (i.e. invalid edge)
            1, if collection_a is the source node and collection_b is the target node (i.e. outbound edge)
        """

        # coll_a = self.transform(collection_a)
        coll_a = collection_a
        # coll_b = self.transform(collection_b)
        coll_b = collection_b

        # Case: Using graph edge definitions
        if use_graph_definition:
            for edge_definition in self.edges:
                source_colls = edge_definition[FROM_VERTEX_COLLECTIONS]
                target_colls = edge_definition[TO_VERTEX_COLLECTIONS]

                # Outbound a -> b
                if (coll_a in source_colls and coll_b in target_colls):
                    return 1

                # Inbound a <- b
                if (coll_a in target_colls and coll_b in source_colls):
                    return -1

        # Case: Using manually provided, custom meta edges
        # TODO load edges/meta edges from database
        #if coll_a in self.meta_edges:
        #    # Outbound a -> b
        #    if coll_b in self.meta_edges[coll_a]:
        #        return 1
        #
        #if coll_b in self.meta_edges:
        #    # Inbound a <- b
        #    if coll_a in self.meta_edges[coll_b]:
        #        return -1
        #
        return 0
    
    def _compose_mixed_edge_directions_statement(self, edges: list) -> str:
        """
        Composes the part of an AQL Graph Traversal statement that specifies the direction for individual edges.
        In ArangoDB, edges are directed. In the GraphFlow however, the traversal direction might be different
        to that of the edge sin the database. For example, if the database contains "Person" - [likes] -> "Food",
        but the traversal direction was specified to be "Food" - [likes] - "Person", then the edge "likes" will have
        to be traversed in the opposite direction (INBOUND).
        #traversing-in-mixed-directions
        See: https://docs.arangodb.com/3.11/aql/graphs/traversals/#traversing-in-mixed-directions

        Approach:
        1. Group edges by their name: All edges of the same type will eventually be assigned with the
        same direction.
        2. For each edge type, identify the required edge direction to use. If the edge type has to be
        traversed only from source to target, apply "OUTBOUND". Else, apply "INBOUND" or "ANY" respectively.
        """

        label_dict = {}

        # Group edges by their name
        for edge in edges:
            name = edge.name
            direction = edge.direction

            if name not in label_dict:
                label_dict[name] = [direction]
            else:
                directions = label_dict[name]
                directions.append(direction)
                label_dict[name] = directions

        # Identify which name has multiple directions
        edge_directions = {}
        for edge_name, directions in label_dict.items():
            unique_directions = list(set(directions))
            if not unique_directions:
                continue
            elif len(unique_directions) > 1:
                edge_directions[edge_name] = ANY
            elif unique_directions[0] == -1:
                edge_directions[edge_name] = INBOUND
            else:
                edge_directions[edge_name] = OUTBOUND

        parts = list()
        for edge_name, direction in edge_directions.items():
            part = f'{direction} {edge_name}'
            parts.append(part)
        stmt = ', '.join(parts)
        return stmt
    
    
    def _build_query_graph_traversal(self,
                                    s2s_paths:list,
                                    bind_vars:dict
                                    ) -> tuple[str, str, dict]:
        
        """
        Builds the AQL part that executes a graph traversal based on the provides source-to-sink paths (s2s_paths).
        """

        # For each path, create a seperate condition (e.g. '(p.vertices[0].name == "Peter")')
        filter_statements = list()
        for path in s2s_paths:
            filter_statement, bind_vars = self._build_aql_path_filter(
                path,
                bind_vars
            )
            filter_statements.append(filter_statement)

        # Step 3: Combine queries
        statements = '\nOR\n'.join(filter_statements)
        aql_filter_statement = f"FILTER ({statements})"

        # Step 4: Add the edge direction part of the graph traversal query
        s2s_paths = self.flow.update_traversal_directions(s2s_paths)
        for edge in self.flow.edges:
            dir = self._edge_direction(
                collection_a=edge.source.collection,
                collection_b=edge.target.collection)
            edge.direction = dir  # -1: inbound, 1: outbound, =: undirected
        dir_stmt = self._compose_mixed_edge_directions_statement(
            self.flow.edges)
        
        return aql_filter_statement, dir_stmt, bind_vars
        

    def generate_aql_graph_query(self, graph_data:GraphData, max_start_nodes:int = 10, max_paths:int = 10) -> tuple[str, dict]:
        """
        This function generates an AQL query that can be used to query the given graph data.

        Arguments:
        - graph_data:dict
            Dictionary containing two lists (`nodes` and `edges`) denoting the graph_template to be queried.
        - max_start_nodes:int
            Maximum number of nodes to start graph traversals from. Can lead to missing paths.
            This will apply a LIMIT clause in the AQL query. To exclude this clause, set to -1.
        - max_paths:int
            Maximum number of paths to traverse before returning the result. Can halt graph traversal prematurely.
            This will apply a LIMIT clause in the AQL query. To exclude this clause, set to -1.
            
        Returns:
        - aql_query:str
            A corresponding ArangoDB query (AQL query) with which the provided graph_data can be queried on the database.  
        """

        print("Preprocessing graph data ...")        
        # Ensure valid format of graph_data
        try:
            self._validate_graph_data(graph_data)
        except Exception as e:
            logger.error(
                f"Validation of graph data failed - Please ensure the correct format. "
                f"Message: {str(e)}")
            return None
        
        # Create GraphFlow object. Will handle operations and calculations on the flow
        nodes = graph_data.get('nodes')
        edges = graph_data.get('edges')
        self.flow = GraphFlow(nodes, edges)        

        # (debug)
        self.flow.print_flow()

        ###### QUERY BUILDING START ######

        # 1. Obtain all source nodes (can be from multiple collections)
        source_nodes = self.flow.find_source_nodes()
        sink_nodes = self.flow.find_sink_nodes()

        # 2. Build first query part to obtain all "start documents" (i.e. all docs from which to start graph traversals)
        bind_vars = dict() # Will contain the parameters for the query

        start_node_query, bind_vars = self._build_query_start_nodes(
            source_nodes,
            max_start_nodes,
            bind_vars
        )

        # 3. Find all paths from start nodes to sink nodes
        source_nodes_edges = [(None, node) for node in source_nodes]
        s2s_paths = self.flow.find_source_to_sink_paths(
            source_nodes_edges, sink_nodes)

        # 4. Build second query part to perform the graph traversal
        aql_filter_statement, dir_stmt, bind_vars = self._build_query_graph_traversal(
            s2s_paths,
            bind_vars
        )

        # 5. Combine the query to obtain start nodes & to obtain the graph traversal paths
        min_depth = 0
        max_depth = len(max(s2s_paths, key=len))-1
        vertex_collections = self.flow.get_vertex_collections()
        #vertex_collections = [self.transform(vertex_name) for vertex_name in vertex_collections]
        edge_collections = self.flow.get_edge_collections()
        # allowed vertex collections to traverse
        bind_vars[VERTEX_COLLECTIONS] = vertex_collections
        # allowed edge collections to traverse
        bind_vars[EDGE_COLLECTIONS] = edge_collections
        # minimum traversal depth
        bind_vars[MIN] = min_depth
        # maximum traversal depth (= longest path)
        bind_vars[MAX] = max_depth
        aql_query = GET_GRAPH.format(
            start_nodes_aql_query=start_node_query,
            start_nodes_var=START_NODES_VAR,
            base_direction=ANY,
            edge_directions=dir_stmt,
            path_filters=aql_filter_statement,
            graph_stmt=f"GRAPH '{self.graph_name}'" if not dir_stmt else "",
            limit=f'LIMIT {max_paths}' if max_paths and max_paths > 0 else ''
        )

        ###### QUERY BUILDING END ######

        # 6. Return query
        return aql_query, bind_vars
    
    def execute_aql_query(self, aql_query:str, bind_vars:dict) -> dict:
        try:
            cursor = self.arango_db.aql.execute(
                aql_query,
                bind_vars=bind_vars,
                cache=False
            )
        except Exception as e:
            logger.info(
                f"Error executinog the AQL query: exception of type {str(type(e))} was thrown. "
                f"Message: {str(e)}"
            )
            raise e

        # return cursor
        return cursor


### Sample Usage:

# Load database config from json file
import json
path_to_config = 'C:/Users/opit_do/Desktop/config.json'
with open(path_to_config, "r") as f:
    config = json.load(f)
my_config = Config(
    url=f'{config["DB_HOST"]}:{config["DB_PORT"]}',
    user=config["DB_USER"],
    password=config["DB_PASSWORD"],
    database=config["DB_NAME"],
    graph=config["DB_GRAPH"],
)

sample_node_1 = {
    "id":"0",
    "collection":"Corpus",
    "userData":[
        {
            "attribute":"name",
            "attributeType":"text",
            "operator": "alphabetic_contains",
            "value":"Wikipedia",
        }
    ]
}

sample_node_2 = {
    "id":"1",
    "collection":"WikiArticle",
    "userData":[
        {
            "attribute":"name",
            "attributeType":"text",
            "operator": "alphabetic_contains",
            "value":"Climate Change",
        }
    ]
}

sample_edge = {
    "id":"reactflow__edge-0-1",
    "source":"0",
    "target":"1",
    "name":"BelongsTo",
    "userData": [
        {
            "attribute":"timestamp",
            "attributeType":"datetime",
            "operator": "date_smaller_than",
            "value":"2023-11-24T23:00:00.000Z",
        }
    ]
}
graph_data = {'nodes': [sample_node_1, sample_node_2], 'edges': [sample_edge]}

query_builder = QueryBuilder(my_config)
aql_query, bind_vars = query_builder.generate_aql_graph_query(graph_data)
print("Graph Traversal Query: ", aql_query)
query_result = query_builder.execute_aql_query(aql_query, bind_vars)
print("Query Result: ", query_result)



### Debug Code End