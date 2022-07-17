from abc import ABC, abstractmethod
from datetime import datetime

from ..component import Component

from cag.utils.config import Config
class AnnotatorBase(ABC, Component):

    def __init__(self, query, run=False,params={}, conf: Config=None):
        super().__init__(conf)
        self.query = query
        self.now = datetime.now()
        self.params={}
        if run:
            self.update_graph(self.now)

    def fetch_annotator_data(self):
        return self.database.AQLQuery(self.query, rawResults=True).response['result']


    @abstractmethod
    def update_graph(self, timestamp):
        g = self.graph

    