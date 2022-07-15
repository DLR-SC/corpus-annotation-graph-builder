import logging
from arango import ViewGetError, ArangoClient

from dataclasses import dataclass, field
from typing import List, ClassVar
from arango.database import StandardDatabase
from graph_framework.utils import utils
from graph_framework.views.link import Link, AnalyzerList, Field


@dataclass()
class ViewProperties():
    cleanupIntervalStep: int =0
    ## Default arango db values
    cleanup_interval_step: int  = 0
    commit_interval_msec: int  = 1000
    consolidation_interval_msec: int  = 0
    # self.consolidation_policy = {
    # type = "tier",
    # segments_min = 1,
    # segments_max = 10,
    # segments_bytes_max = 5368709120,
    # segments_bytes_floor = 2097152,
    # min_score = 0}
    primary_sort_compression: str = "lz4"
    writebuffer_idle : int = 64
    writebuffer_active: int  = 0
    writebuffer_max_size: int  = 33554432



@dataclass
class View():
    name:str
    view_type:str = "arangosearch"
    properties: ViewProperties = field(default_factory = lambda:ViewProperties())
    links: List[Link] = field(default_factory = lambda:[])
    primary_sort : List = field(default_factory = lambda:[])
    stored_values: List = field(default_factory = lambda:[])

    _MANDATORY_FIELDS:ClassVar = ["name", "view_type"]

    def add_primary_sort(self, field_name:str, asc:bool):
        self.primary_sort.append({"field": field_name, "asc": asc})

    def add_stored_value(self, fields:[], compression ="lz4"):
        for field_name in fields:
            self.stored_values.append({"fields": [field_name], "compression": compression})

    def add_link(self, link: Link):
        self.links.append(link)

    def get_links_dict(self):
        dict_ = {}
        for l in self.links:
            dict_.update(l.summary())
        return dict_

    def get_properties(self) -> dict:
        mandatory_fields = View._MANDATORY_FIELDS
        result = utils.camel_nest_dict(utils.filter_dic(self))
        result["links"] = self.get_links_dict()
        for mandatory in mandatory_fields:
            del result[utils.camel_case(mandatory)]
        return result

    def summary(self) -> dict:
        result = utils.camel_nest_dict(utils.filter_dic(self))
        result["links"] = self.get_links_dict()
        return result

    def create(self, database: StandardDatabase):
        result = database.create_view(self.name,
                                      self.view_type,
                                      self.get_properties())
        return result

## TEST REMOVE THIS TO ANOTHER PLACE
def main():
    # Connect to "test" database as root user.
    client = ArangoClient()

    db = client.db('InsightsNet', username='root', password='')
    link = Link(name="TextNode")
    linkAnalyzers = AnalyzerList(["identity"])
    link.analyzers = linkAnalyzers

    # fields
    field1 = Field("text", AnalyzerList(["text_en", "invalid_analyzer"]))
    print(field1.analyzers)
    field1.analyzers.filter_invalid_analyzers(db, verbose=1)
    print(field1.analyzers)

    link.add_field(field1)
    logging.info(link.get_fields_dict())

    view = View('basic_view_linked_withprops',
                view_type="arangosearch")
    view.add_link(link)
    view.add_primary_sort("text", asc = False)
    #
    view.add_stored_value(["text", "timestamp"], compression="lz4")

    logging.info(view.summary())
    view.create(db)

if __name__ == "__main__":
    main()