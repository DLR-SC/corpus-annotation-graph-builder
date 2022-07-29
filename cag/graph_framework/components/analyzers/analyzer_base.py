from abc import ABC, abstractmethod
from dataclasses import dataclass
from pyvis.network import Network
import networkx as nx
from cag.utils.config import Config
from cag.graph_framework.components.component import Component
from enum import Enum
from pyArango.query import AQLQuery


class AnalyzerMode(Enum):
    NOTEBOOK = 1
    HTML = 2
    MATPLOTLIB = 3


@dataclass
class Doc:
    _id: str
    _key: str


@dataclass
class EdgeDoc(Doc):
    _from: str
    _to: str
    _id: str
    _key: str


@dataclass
class PathElement:
    vertices: 'list[Doc]'
    edges: 'list[EdgeDoc]'


class AnalyzerBase(ABC, Component):
    def __init__(self, config: Config, mode: AnalyzerMode = AnalyzerMode.NOTEBOOK, run=False, query: "None|str" = None) -> None:
        super().__init__(config)
        self.mode = mode
        self.data = []
        self.query = query
        if self.query:
            self.data = self.database.AQLQuery(self.database, self.query)
        if run:
            self.run()

    @abstractmethod
    def run():
        pass

    def create_networkx(self, graph_data: list[PathElement], weight_edges=False) -> nx.Graph:
        G = nx.Graph()
        for p in graph_data:
            for v in p.vertices:
                G.add_node(v._id, **v)
            for e in p.edges:
                if weight_edges:
                    G.add_edge(e._from, e._to, **e)
                else:
                    if G.has_edge(e._from, e._to):
                        G.get_edge_data(e._from, e._to)['weight'] += 1
                    else:
                        G.add_edge(e._from, e._to, weight=1, **e)
        return G

    def visualize_graph(self, graph_data: list[PathElement], weight_edges=False) -> Network:
        G = self.create_networkx(graph_data, weight_edges)
        g = Network(notebook=(self.mode == AnalyzerMode.NOTEBOOK))
        g.from_nx(G)
        return g
