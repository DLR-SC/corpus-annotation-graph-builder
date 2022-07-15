import logging
import logging
logging.basicConfig(level = logging.INFO)
from dataclasses import dataclass, field
from arango.database import StandardDatabase
from graph_framework.utils import utils
from arango import ArangoClient,  AnalyzerGetError
from nltk.corpus import stopwords
from typing import List, ClassVar


@dataclass
class EdgeNGram:
    min: int = 2
    max: int = 4
    preserve_original: bool = True

    def summary(self):
        result = utils.camel_nest_dict(utils.filter_dic(self))
        return result


@dataclass
class ArangoAnalyzer():
    #####################
    ### Instance Vars ###
    #####################
    name: str
    type:str = "identity"
    features: List = field(default_factory=lambda: ["frequency", "norm", "position"])

    ## Properties - loaded based on type
    # TEXT
    locale: str = "en"  # text, stem, norm
    case: str = "lower"  # text,  norm
    stopwords: List = field(default_factory=lambda: [])
    accent: bool = False  # text,  norm
    stemming: bool = True
    edge_ngram: "EdgeNGram | None" = None  #
    # type: delimiter
    delimiter: str = ','

    # type ngram
    min: int = 2
    max: int= 5
    preserve_original: bool = False
    start_marker: str = ""
    end_marker: str = ""
    stem_type: str = field(default_factory=lambda:ArangoAnalyzer._STEM_TYPE_BINARY)


    #################
    ### CONSTANTS ###
    #################

    ######################################
    ### Main types of arango analyzer ###
    #####################################
    _TYPE_IDENTITY: ClassVar = "identity"
    _TYPE_TEXT: ClassVar = "text"
    _TYPE_NGRAM: ClassVar ="ngram"
    _TYPE_STEM: ClassVar = "stem"
    _TYPE_NORM: ClassVar = "norm"
    _TYPE_DELIMITER: ClassVar ="delimiter"

    # For type Stem - there are 2 stem types
    _STEM_TYPE_BINARY: ClassVar = "binary"
    _STEM_TYPE_UTF8: ClassVar = "utf8"

    _MANDATORY_FIELDS: ClassVar = ['name', 'type', 'features']

    FIELDS: ClassVar = {
        _TYPE_IDENTITY : [],
        _TYPE_TEXT: ['locale', 'case', 'stopwords', 'accent', 'stemming', 'edge_ngram'],
        _TYPE_NGRAM: ['min', 'max', 'preserve_original',
                      'start_marker', 'end_marker', 'stem_type'],
        _TYPE_STEM: ['locale'],
        _TYPE_DELIMITER: ['delimiter'],
    }

    #############
    ## Setters ##
    #############
    def set_features(self, frequency= True, norm=True, position = True):
        '''
        Sets which features to return - It is set to have all three features: frequency, norm and position
        :param frequency: bool
        :param norm: bool
        :param position: bool
        :return:
        '''
        features = []
        if frequency: features.append("frequency")
        if norm: features.append("norm")
        if position: features.append("position")
        self.features = features

    def set_edge_ngrams(self, min =2, max = 5, preserve_original = False):
        self.edge_ngram =  EdgeNGram(min =min, max = max, preserve_original = preserve_original)


    def set_stopwords(self, language = "english", custom_stopwords= [], include_default = True):
        logging.info('The default stopword list is loaded from NLTK - if you get an error, run `nltk.download('
                     '"stopwords")`')
        if include_default:
            self.stopwords = stopwords.words(language)

        if len(custom_stopwords) > 0:
            self.stopwords.extend(custom_stopwords)


    #############
    ## Getters ##
    #############
    def get_type_fields(self) -> []:
        '''
        Gets the list of fields needed and set for the Analyzer based on the Type

        :return: list of fields
        '''
        return ArangoAnalyzer.FIELDS[self.type]

    def get_properties(self) -> dict:
        keep = ArangoAnalyzer.FIELDS[self.type]
        result =utils.camel_nest_dict(utils.filter_dic(self,keep))
        return result

    def summary(self) -> dict:
        keep = ArangoAnalyzer._MANDATORY_FIELDS + ArangoAnalyzer.FIELDS[self.type]
        result =utils.camel_nest_dict(utils.filter_dic(self,keep))
        return result


    def create(self, database: StandardDatabase):
        result = {}
        try:
            info = database.analyzer(self.name)
            logging.error("Analyzer {} already exists with the following info: {}".format(self.name, info))
            logging.error("You can delete it first using *database.delete_analyzer({})* and that create".format(self.name))
        except AnalyzerGetError:
            result = database.create_analyzer(self.name,
                                              self.type,
                                              self.get_properties(),
                                              self.features)
            logging.info("Analyzer was created!")
        return result




## TEST REMOVE THIS TO ANOTHER PLACE
def main():
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('InsightsNet', username='root', password='p3yqy8I0dHkpOrZs')

    b = ArangoAnalyzer("TheText_STOP_new")
    b.set_stopwords(language="english", custom_stopwords=['added', 'YOUPPPPPYYY'], include_default=True)
    b.type = ArangoAnalyzer._TYPE_TEXT

    b.create(db)

    #print(db.analyzer('TheText_STOP_newas'))

if __name__ == "__main__":
    main()