from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from cag.framework.component import Component
from pyArango.collection import Document
from pyArango.query import AQLQuery
from cag.utils.config import Config


class GenericAnnotator(ABC, Component):
    def __init__(self, query: str, run=False, params={}, conf: Config = None, fetch_args: "dict[str,Any]" = {}, filter_annotatable=False,
                 annotator_fieldname="_annotator_params"):
        """the base class to extend your annotator from

        :param query: an arango query valid on your DB, returing the `annotator_fieldname` on the root-elements as a field from the docs to update
        :type query: str
        :param run: whether to run the analyzer on init, defaults to False
        :type run: bool, optional
        :param params: the parameters to set/check for on update, defaults to {}
        :type params: dict, optional
        :param conf: the config+connection to use, defaults to None
        :type conf: Config, optional
        :param fetch_args: the AQLQuery parameters (batch_size, etc.), defaults to {}
        :type fetch_args: dict[str,Any], optional
        :param filter_annotatable: Whether to filter your annotations, defaults to False
        :type filter_annotatable: bool, optional
        :param annotator_fieldname: the field to set your params on and filter the data, defaults to "_annotator_params"
        :type annotator_fieldname: str, optional
        """
        super().__init__(conf)
        self.annotator_fieldname = annotator_fieldname
        self.query = query
        self.now = datetime.now()
        self.params = params
        self.filter_annotatable = filter_annotatable
        if fetch_args is not None:
            self.fetch_args = fetch_args
        else:
            self.fetch_args = {}
        data = None
        if self.query is not None:
            data = self.fetch_annotator_data()
        if run:
            self.update_graph(self.now, data)

    def fetch_annotator_data(self):
        if self.filter_annotatable:
            query_modified = f"""
            LET annotator_data=({self.query})
            FOR dp IN annotator_data
                FILTER dp.{self.annotator_fieldname} == NULL or dp.{self.annotator_fieldname}!=@params
                RETURN dp
            """
            return self.database.AQLQuery(query_modified, bindVars={'params': self.params}, **self.fetch_args)
        else:
            return self.database.AQLQuery(self.query, **self.fetch_args)

    def complete_annotation(self, doc: Document):
        return self.upsert_node(doc.collection.name, doc.getStore())

    def upsert_node(self, collectionName: str, data: "dict[str, Any]", alt_key: "str | []" = None) -> Document:
        data[self.annotator_fieldname] = self.params
        return super().upsert_node(collectionName, data, alt_key)

    @abstractmethod
    def update_graph(self, timestamp, data: AQLQuery):
        g = self.graph

    def query_count(self)->int:
        """Get the total count of the query provided

        :return: the count of documents that *would* be returned
        :rtype: int
        """        """"""
        if self.query is None:
            return -1
        count_query = self.database.AQLQuery(f"""
LET query=({self.query})
RETURN COUNT(query)
        """, rawResults=True)
        return count_query[0]

    def load_page(self, offset: int = 0, limit: int = 500) -> AQLQuery:
        """Load a single page from the provided query

        :param offset: the offset to keep, defaults to 0
        :type offset: int, optional
        :param limit: the limit of the page, defaults to 500
        :type limit: int, optional
        :return: the executed query with the page (batchSize=limit, rawResults=True)
        :rtype: AQLQuery
        """""""""
        if self.query is None:
            return -1
        page_query = self.database.AQLQuery(f"""
LET query=({self.query})
FOR d IN query
    LIMIT @offset,@limit
    RETURN d
        """, bindVars={'offset': offset, 'limit': limit}, rawResults=True, batch_size=limit)
        return page_query
