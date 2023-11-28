from objects.Node import Node

class Edge:
    def __init__(self,
                 id:str,
                 source:Node,
                 target:Node,
                 name:str,
                 conditions:list):
        # Edge id
        self.id:str = id

        # Source node (object)
        self.source:Node = source

        # Target node (object)
        self.target:Node = target

        # Edge name (i.e. the name of the collection that this edge is given in ArangoDB)
        self.name:str = name

        # Edge filters. Each item is a separate condition
        self.conditions:list = conditions

        # Edge direction (ingoing, outgoing)
        self.direction:int = None