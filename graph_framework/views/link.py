import logging

from graph_framework.utils import utils

logging.basicConfig(level = logging.DEBUG)

from dataclasses import field, dataclass
from typing import List

from arango import AnalyzerGetError
from arango.database import StandardDatabase

@dataclass
class AnalyzerList:
    analyzerList: List = field(default_factory=lambda:[])  # ["text_en"]

    def get_invalid_analyzers(self, database: StandardDatabase, verbose=0):
        invalid_analyzer = []
        for analyzer in self.analyzerList:
            try:
                info = database.analyzer(analyzer)
                if verbose == 1:
                    print(info)
            except AnalyzerGetError:
                invalid_analyzer.append(analyzer)
        return invalid_analyzer

    def filter_invalid_analyzers(self, database: StandardDatabase, verbose:int=0):

        invalid_analyzer = self.get_invalid_analyzers(database)
        if verbose == 1:
            logging.warning("Filtered out the following invalid analyzers: "+ str(invalid_analyzer))
        self.analyzerList = [a for a in self.analyzerList if a not in invalid_analyzer]

@dataclass
class Field():
    field_name: str
    analyzers:AnalyzerList = field(default_factory=lambda:AnalyzerList())

    def get_field(self):
        dict_ = {}
        dict_[self.field_name] = {"analyzers": self.analyzers.analyzerList}
        return dict_



@dataclass

class Link():
    '''
     link = {
      "includeAllFields": True,
      "fields" : { "description" : { "analyzers" : [ "text_en" ] } }
    }

    '''

    name: str
    include_all_fields: bool = False
    store_values:str =  None
    track_list_positions: bool = False
    fields: List[Field] = field(default_factory =  lambda:[])#["text_en"]
    analyzers:AnalyzerList = field(default_factory=lambda:AnalyzerList(["identity"]))

    def add_field(self, field:Field):
        self.fields.append(field)

    def get_fields_dict(self):
        dict_ = {}
        for f in self.fields:
            dict_.update(f.get_field())

        return dict_

    def summary(self):
        '''
        Return Link as dictionary to be used in arango
        :return:
        '''
        keep = ['include_all_fields', 'store_values', 'track_list_positions']
        dict_  =  {}
        dict_[self.name] = {}
        dict_[self.name]["analyzers"] = self.analyzers.analyzerList
        dict_[self.name]["fields"] = self.get_fields_dict()
        dict_[self.name].update(utils.camel_nest_dict(utils.filter_dic(self, keep)))


        return dict_





