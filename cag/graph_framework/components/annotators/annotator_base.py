from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from ..component import Component
from pyArango.collection import Document
from pyArango.query import AQLQuery
from cag.utils.config import Config
class AnnotatorBase(ABC, Component):
    def __init__(self, query, run=False, params={}, conf: Config=None, fetch_args:"dict[str,Any]"={}, filter_annotatable=False,
        annotator_fieldname="_annotator_params"):
        super().__init__(conf)
        self.annotator_fieldname=annotator_fieldname
        self.query = query
        self.now = datetime.now()
        self.params=params
        self.filter_annotatable=filter_annotatable
        if fetch_args is not None:
            self.fetch_args=fetch_args
        else:
            self.fetch_args={}
        if run:
            self.update_graph(self.now, self.fetch_annotator_data())

    def fetch_annotator_data(self):
        if self.filter_annotatable:
            query_modified=f"""
            LET annotator_data=({self.query})
            FOR dp IN annotator_data
                FILTER dp.{self.annotator_fieldname} == NULL or dp.{self.annotator_fieldname}!=@params
                RETURN dp
            """
            return self.database.AQLQuery(query_modified,bindVars={'params':self.params}, **self.fetch_args)
        else:
            return self.database.AQLQuery(self.query, **self.fetch_args)

    def complete_annotation(self, doc:Document):
        return self.upsert_vert(doc.collection.name, doc.getStore())
    def upsert_vert(self, collectionName: str, data: "dict[str, Any]", alt_key: "str | []" = None) -> Document:
        data[self.annotator_fieldname]=self.params
        return super().upsert_vert(collectionName, data, alt_key)
    @abstractmethod
    def update_graph(self, timestamp, data:AQLQuery):
        g = self.graph

    