import logging

from graph_framework.utils import utils
from graph_framework.view_wrapper.arango_analyzer import AnalyzerList

logging.basicConfig(level = logging.DEBUG)

from dataclasses import field, dataclass
from typing import List

@dataclass
class Field():
    field_name: str
    analyzers:AnalyzerList = field(default_factory=lambda:AnalyzerList())

    def summary(self):
        dict_ = {}
        dict_[self.field_name] = {"analyzers": self.analyzers.analyzerList}
        return dict_

@dataclass
class Link():
    '''
    Check attributes documentations here https://www.arangodb.com/docs/stable/arangosearch-views.html
    '''
    name: str
    include_all_fields: bool = False
    store_values:str =  None
    track_list_positions: bool = False
    in_background: bool = False
    fields: List[Field] = field(default_factory =  lambda:[])
    analyzers:AnalyzerList = field(default_factory=lambda:AnalyzerList(["identity"]))

    def add_field(self, field:Field):
        self.fields.append(field)

    def get_fields_dict(self):
        dict_ = {}
        for f in self.fields:
            dict_.update(f.summary())
        return dict_

    def summary(self):
        '''
        Return Link as dictionary to be used in arango
        :return:
        '''
        keep = ['include_all_fields', 'store_values', 'track_list_positions', 'in_background']
        dict_  =  {}
        dict_[self.name] = {}
        dict_[self.name]["analyzers"] = self.analyzers.analyzerList
        dict_[self.name]["fields"] = self.get_fields_dict()
        dict_[self.name].update(utils.camel_nest_dict(utils.filter_dic(self, keep)))

        return dict_





