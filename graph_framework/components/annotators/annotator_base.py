from abc import ABC, abstractmethod
from datetime import datetime

from ..component import Component


class AnnotatorBase(ABC, Component):

    def __init__(self, database, query, run=False,params={}):
        super().__init__(database)
        self.query = query
        self.now = datetime.now()
        self.params={}
        if run:
            self.update_graph(self.now)



    @abstractmethod
    def update_graph(self, timestamp):
        g = self.graph

    