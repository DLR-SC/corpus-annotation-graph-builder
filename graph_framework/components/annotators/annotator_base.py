from abc import ABC, abstractmethod
from datetime import datetime

from ..component import Component

from ...utils.config import Config
class AnnotatorBase(ABC, Component):

    def __init__(self, query, run=False,params={}, conf: Config=None):
        super().__init__(conf)
        self.query = query
        self.now = datetime.now()
        self.params={}
        if run:
            self.update_graph(self.now)



    @abstractmethod
    def update_graph(self, timestamp):
        g = self.graph

    