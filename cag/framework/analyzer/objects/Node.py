class Node:
    
    def __init__(self,
                 id:str,
                 collection:str,
                 conditions:list):
        # Node id
        self.id:str = id

        # Node collection
        self.collection:str = collection

        # Node filters
        self.conditions:list = conditions
    