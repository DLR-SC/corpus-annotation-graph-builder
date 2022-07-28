from cag.graph_framework.graph.base_graph import BaseGraph

from pyArango.graph import Graph, EdgeDefinition

class SampleGraph(BaseGraph):
    _edgeDefinitions = [EdgeDefinition('GenericEdge', fromCollections=['GenericNode'], toCollections=['GenericNode'])]
    _orphanedCollections = []
    
