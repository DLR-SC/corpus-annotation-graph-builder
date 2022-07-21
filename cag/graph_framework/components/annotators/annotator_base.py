from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from ..component import Component

from cag.utils.config import Config
class AnnotatorBase(ABC, Component):

    def __init__(self, query, run=False,params={}, conf: Config=None, fetch_args:"dict[str,Any]"={}):
        super().__init__(conf)
        self.query = query
        self.now = datetime.now()
        self.params={}
        if fetch_args is not None:
            self.fetch_args=fetch_args
        else:
            self.fetch_args={}
        if run:
            self.update_graph(self.now)

    def fetch_annotator_data(self):
        return self.database.AQLQuery(self.query, **self.fetch_args)


    @abstractmethod
    def update_graph(self, timestamp):
        g = self.graph

    