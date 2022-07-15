#import logging

from arango import ViewGetError, ArangoClient

#logging.basicConfig(level = logging.DEBUG)

from dataclasses import dataclass, field
from typing import List, ClassVar
from arango.database import StandardDatabase
from graph_framework.utils import utils


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
class SortingField:
    name: str
    asc: bool = True

@dataclass
class View():
    name:str
    view_type:str = "arangosearch"
    properties: ViewProperties = field(default_factory = lambda: ViewProperties())
    links: dict = field(default_factory = lambda: {})
    primary_sort : List = field(default_factory = lambda: [SortingField])
    stored_values: List = field(default_factory = lambda: [])

    _MANDATORY_FIELDS:ClassVar = ["name", "view_type"]

    def get_properties(self) -> dict:
        keep = View._MANDATORY_FIELDS
        result = utils.camel_nest_dict(utils.filter_dic(self, keep))
        return result

    def summary(self) -> dict:
        result = utils.camel_nest_dict(utils.filter_dic(self))
        return result

    def create(self, database: StandardDatabase):
        result = database.create_view(self.name,
                                      self.view_type,
                                      self.get_properties())
        return result

## TEST REMOVE THIS TO ANOTHER PLACE
def main():
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('InsightsNet', username='root', password='p3yqy8I0dHkpOrZs')

    basicView = View('basic_view')
    print(basicView.get_properties())
    basicView.create(db)

    print(db.view('basic_view'))
