from objects.Node import Node
from objects.Edge import Edge
from collections import deque
from itertools import chain

# Logging Setup
import sys
import logging
import colorlog
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fmt = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s | %(asctime)s | %(message)s")
stdout = colorlog.StreamHandler(stream=sys.stdout)
stdout.setFormatter(fmt)
logger.addHandler(stdout)


class GraphFlow:
    """
    A GraphFlow is the internal representation of a graph. It is used by the QueryBuilder to
    generate a AQL query that retrieves the represented graph data. It contains all nodes and edes
    and provides functions to work with them.
    """

    def __init__(self, nodes: list, edges: list, name: str = "Flow"):
        self.name = name
        self.nodes = list()
        self.edges = list()
        # Will be filled later on once the root node has been identified
        self.depth_dict = dict()

        # Build internal representation of the QGV
        self._build_from_json(nodes, edges)

    def _are_nodes_connected(self, node1: Node, node2: Node):
        """
        Checks whether the two given collections are connected in the GraphFlow.

        Args:
            node1 (Node): collection name 1
            node2 (Node): collection name 2

        Returns:
            bool: Whether node1 and node2 are connected in the GraphFlow.
        """
        
        return any(lambda edge: (
            (edge.source == node1 and edge.target == node2) or
            (edge.source == node2 and edge.target == node1)
        ))
    
    def get_vertex_collections(self):
        """
        Gets a list of all vertex collection names in this GraphFlow.

        Returns:
            list: List of collection names
        """
        vertex_names = [node.collection for node in self.nodes]
        return list(set(vertex_names))

    def get_edge_collections(self):
        """
        Gets a list of all edge collection names in this GraphFlow.

        Returns:
            list: List of collection names
        """
        edge_names = [edge.name for edge in self.edges]
        return list(set(edge_names))

    def update_traversal_directions(self, paths:list) -> list:
        """
        Inheritly, edges of a GraphFlow have a direction from source to target. This is
        specified in the Edge objects themselve (they have a "source" and "target" property).

        This is fine if the desired traversal direction is from from source nodes to target nodes,
        i.e. from left to right. However, there might be scenarios where the desired traversal
        direction is different, e.g. for performance reasons. In this case, the edge direction
        must be adjusted to match the corresponding paths.

        A path is a sequence of (edge,node) pairs. The order of these pairs corresponds to the
        traversal order of the AQL query. Hence, any (edge) should have its corresponding (node)
        as the target. If that is not the case, the direction of (edge) is switched.

        Args:
            paths (list): List of lists. Each sublist contains (edge,node) pairs.

        Returns:
            list: The same list that was passed to this function, but with the adjusted edge directions.
        """

        for path in paths:
            """
            A path contains tuples of (edge, node). 'edge' is the incoming edge pointing to 'node'.
            Node is a target node of the edge.
            If, however, the node is present at the source instead, the edge direction needs
            to be switched.
            """

            # For each edge/node pair in the path
            for edge, target_node in path:

                # First node of the path is a source node, i.e. no incoming edges
                if not edge:
                    continue

                # If the edge direction does not correspond to the desired traversal direction, switch
                if edge.source == target_node:
                    tmp = edge.target
                    edge.source = edge.target
                    edge.target = tmp
        return paths


    def _dfs(self, node, visited):
        """
        Helper function for self.is_graph_connected()
        """
        
        # Mark the current node as visited
        visited[node] = True

        # Recur for all adjacent nodes (neighbors)
        for edge in self.edges:
            if edge.source == node or edge.target == node:
                neighbor = edge.target if edge.source == node else edge.source
                if not visited[neighbor]:
                    self._dfs(neighbor, visited)

    def is_graph_connected(self) -> bool:
        """
        Checks whether the graph has any unconnected subgraphs. Performs a dfs on the
        graph starting with a random node. If not all nodes were visited during dfs, then the
        flow is considered to contain unconnected subgraphs.

        Returns:
            bool: Whether or not the graph is connected.
        """

        # Dictionary to keep track of visited nodes
        visited = {node: False for node in self.nodes}

        # Perform DFS starting from any random node in the graph
        start_node = self.nodes[0]  # Get the first node in the list of nodes
        self._dfs(start_node, visited)

        # If all nodes have been visited, the graph is connected
        return all(visited.values())

    def _build_from_json(self, nodes: list, edges: list) -> None:
        """
        Builds the GraphFlow from nodes and edges given as json objects.

        Args:
            nodes (list): List of nodes, each containing a node id ('id'),
            collection name ('collection') and conditions/filters ('userData')
        """

        # Create the Node objects
        for node in nodes:
            node_obj = Node(id=node['id'],
                            collection=node['collection'],
                            conditions=node['userData'],
                            )
            self.nodes.append(node_obj)

        # Create the Edge objects
        for edge in edges:
            source_id = edge['source']
            target_id = edge['target']
            source_node = next(
                (node for node in self.nodes if node.id == source_id), None)
            target_node = next(
                (node for node in self.nodes if node.id == target_id), None)
            edge = Edge(id=edge['id'],
                        source=source_node,
                        target=target_node,
                        name=edge['name'],
                        conditions=edge['userData'])
            self.edges.append(edge)
    
    def find_edges_by_node(self, node) -> list[Edge]:
        """
        Finds all edges outgoing from the given 'node' (i.e. all edges where 'node' is the source)

        Args:
            node (Node): Node to find the edges for

        Returns:
            list: List of neighboring edges.       
        """

        node_edges = list()
        for edge in self.edges:
            if edge.source == node:
                node_edges.append(edge)
        return node_edges

    def print_flow(self):
        """
        Pretty prints the current GraphFlow.
        """
        
        visited_edges = set()

        for node in self.nodes:
            neighbors = []
            for edge in self.edges:
                if edge.source == node and edge not in visited_edges:
                    neighbors.append((edge, edge.target))
                    visited_edges.add(edge)
            if neighbors:
                for neighbor_edge, neighbor_node in neighbors:
                    print(
                        f"{node.collection} (ID: {node.id}) - [{neighbor_edge.id}] - {neighbor_node.collection} (ID: {neighbor_node.id})")

    def find_source_nodes(self) -> list[Node]:
        """
        Finds and returns all source nodes in the flow.
        A source node is a node that has no incoming connections.

        Returns:
            list: List of source nodes
        """

        # Create a set of all target nodes in edges
        target_nodes = set(edge.target for edge in self.edges)

        # Filter nodes that are not in the set of target nodes
        nodes_without_incoming_edges = [node for node in self.nodes if node not in target_nodes]

        return nodes_without_incoming_edges
    
    def find_sink_nodes(self) -> list[Node]:
        """
        Finds and returns the sink nodes in the flow.
        A sink node is a node that has no outgoing connections.

        Returns:
            list: List of sink nodes
        """

        # Create a set of all source nodes in edges
        source_nodes = set(edge.source for edge in self.edges)

        # Filter nodes that are not in the set of source nodes
        nodes_without_outgoing_edges = [node for node in self.nodes if node not in source_nodes]

        return nodes_without_outgoing_edges
    
    def find_source_to_sink_paths(self, source_nodes, sink_nodes, path=[], edge=None):
        """
        Finds all source-to-sink paths in the GraphFlow.
        A single source-to-sink path is a sequence of edges and nodes leading from a single
        source node to a single sink node.
        The same source and sink nodes can be part of many source-to-sink paths.

        Args:
            source_nodes (list): List of source nodes
            sink_nodes (list): List of sink nodes
            path (list): Current source-to-sink path at some recursion depth.
            Initially an empty list as this is a recursive function.
            edge (Edge): Current edge to traverse at some recursion depth.
            Initially None as this is a recursive function.
        """
        
        if not path:
            path = []

        paths = []
        for edge, node in source_nodes:
            new_path = path + [(edge, node)]
            if node in sink_nodes:
                paths.append(new_path)
            neighbors = [(edge, edge.target) for edge in self.edges if edge.source == node]
            paths.extend(self.find_source_to_sink_paths(neighbors, sink_nodes, new_path, edge))

        return paths

