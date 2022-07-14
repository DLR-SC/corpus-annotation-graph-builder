import logging

from arango.database import StandardDatabase
from graph_framework.utils import utils
from arango import ArangoClient
from nltk.corpus import stopwords


class EdgeNGram(object):

    def __init__(self, min = 2, max=4, preserve_original = False):
        self.min = min
        self.max = max
        self.preserve_original = preserve_original

    def summary(self):
        result = utils.camel_nest_dict(utils.filter_dic(self))
        return result


class ArangoAnalyzer():

    #################
    ### CONSTANTS ###
    #################

    ######################################
    ### Main types of arango analyzer ###
    #####################################
    _TYPE_IDENTITY = "identity"
    _TYPE_TEXT = "text"
    _TYPE_NGRAM ="ngram"
    _TYPE_STEM = "stem"
    _TYPE_NORM = "norm"
    _TYPE_DELIMITER ="delimiter"

    # For type Stem - there are 2 stem types
    _STEM_TYPE_BINARY = "binary"
    _STEM_TYPE_UTF8 = "utf8"


    _MANDATORY_FIELDS = ['name', 'type', 'features']

    FIELDS = {
        _TYPE_IDENTITY : [],
        _TYPE_TEXT: ['locale', 'case', 'stopwords', 'accent', 'stemming', 'edge_ngram'],
        _TYPE_NGRAM: ['min', 'max', 'preserve_original',
                      'start_marker', 'end_marker', 'stem_type'],
        _TYPE_STEM: ['locale'],
        _TYPE_DELIMITER: ['delimiter'],
    }

    def __init__(self, name= "sample_analyzer", type = _TYPE_IDENTITY):

        self.name = name
        self.type = type
        self.features = ["frequency", "norm", "position"]

        ## Properties - loaded based on type
        # TEXT
        self.locale = "en" # text, stem, norm
        self.case = "lower" # text,  norm
        self.stopwords = []
        self.accent = False # text,  norm
        self.stemming = True
        self.edge_ngram = None #
        # type: delimiter
        self.delimiter = ','

        # type ngram
        self.min = 2
        self.max = 5
        self.preserve_original = False
        self.start_marker = ""
        self.end_marker = ""
        self.stem_type = ArangoAnalyzer._STEM_TYPE_BINARY

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
        database.create_analyzer(self.name,
                        self.type,
                        self.get_properties(),
                                 self.features)



## TEST REMOVE THIS TO ANOTHER PLACE
def main():
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('InsightsNet', username='root', password='')

    b = ArangoAnalyzer("TheText_STOP")
    b.set_stopwords(language="english", custom_stopwords=['added', 'YOUPPPPPYYY'], include_default=False)
    b.type = ArangoAnalyzer._TYPE_TEXT
    #b.set_edge_ngrams(min=2, max=5, preserve_original=True)
    print("\n################")
    print(b.get_properties())

    print(utils.filter_dic(EdgeNGram(), ['min']))
    #b.create(db)

if __name__ == "__main__":
    main()