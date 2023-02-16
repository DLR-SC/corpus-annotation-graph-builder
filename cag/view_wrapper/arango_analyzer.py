from dataclasses import dataclass, field
from arango.database import StandardDatabase

from cag import logger
from cag.utils import utils
from arango import AnalyzerGetError
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
class ArangoAnalyzer:

    ###################
    # Instance Vars ###
    ###################
    
    name: str
    type: str = "identity"
    features: List = field(
        default_factory=lambda: ["frequency", "norm", "position"]
    )

    # Properties - loaded based on type
    # TEXT
    locale: str = "en"  # text, stem, norm
    case: str = "lower"  # text,  norm
    stopwords: List = field(default_factory=lambda: [])
    accent: bool = False  # text,  norm
    stemming: bool = True
    edge_ngram: EdgeNGram = None
    delimiter: str = ","

    # type ngram
    min: int = 2
    max: int = 5
    preserve_original: bool = False
    start_marker: str = ""
    end_marker: str = ""
    stem_type: str = field(
        default_factory=lambda: ArangoAnalyzer._STEM_TYPE_BINARY
    )

    #############
    # CONSTANTS #
    #############

    #################################
    # Main types of arango analyzer #
    #################################
    _TYPE_IDENTITY: ClassVar = "identity"
    _TYPE_TEXT: ClassVar = "text"
    _TYPE_NGRAM: ClassVar = "ngram"
    _TYPE_STEM: ClassVar = "stem"
    _TYPE_NORM: ClassVar = "norm"
    _TYPE_DELIMITER: ClassVar = "delimiter"

    # For type Stem - there are 2 stem types
    _STEM_TYPE_BINARY: ClassVar = "binary"
    _STEM_TYPE_UTF8: ClassVar = "utf8"

    _MANDATORY_FIELDS: ClassVar = ["name", "type", "features"]

    FIELDS: ClassVar = {
        _TYPE_IDENTITY: [],
        _TYPE_TEXT: [
            "locale",
            "case",
            "stopwords",
            "accent",
            "stemming",
            "edge_ngram",
        ],
        _TYPE_NGRAM: [
            "min",
            "max",
            "preserve_original",
            "start_marker",
            "end_marker",
            "stem_type",
        ],
        _TYPE_STEM: ["locale"],
        _TYPE_DELIMITER: ["delimiter"],
    }

    #############
    ## Setters ##
    #############
    def set_features(self, frequency=True, norm=True, position=True):
        """
        Sets which features to return - It is set to have all three features: frequency, norm and position
        :param frequency: bool
        :param norm: bool
        :param position: bool
        :return:
        """
        features = []
        if frequency:
            features.append("frequency")
        if norm:
            features.append("norm")
        if position:
            features.append("position")
        self.features = features

    def set_edge_ngrams(self, min=2, max=5, preserve_original=False):
        self.edge_ngram = EdgeNGram(
            min=min, max=max, preserve_original=preserve_original
        )

    def set_stopwords(
        self, language="english", custom_stopwords=[], include_default=True
    ):
        logger.info(
            "The default stopword list is loaded from NLTK - if you get an error, run `nltk.download("
            '"stopwords")`'
        )
        if include_default:
            self.stopwords = stopwords.words(language)

        if len(custom_stopwords) > 0:
            self.stopwords.extend(custom_stopwords)

    #############
    ## Getters ##
    #############
    def get_type_fields(self) -> List:
        """
        Gets the list of fields needed and set for the Analyzer based on the Type

        :return: list of fields
        """
        return ArangoAnalyzer.FIELDS[self.type]

    def get_properties(self) -> dict:
        keep = ArangoAnalyzer.FIELDS[self.type]
        result = utils.camel_nest_dict(utils.filter_dic(self, keep))
        return result

    def summary(self) -> dict:
        keep = (
            ArangoAnalyzer._MANDATORY_FIELDS + ArangoAnalyzer.FIELDS[self.type]
        )
        result = utils.camel_nest_dict(utils.filter_dic(self, keep))
        return result

    def create(self, database: StandardDatabase):
        result = {}
        try:
            info = database.analyzer(self.name)
            logger.error(
                "Analyzer {} already exists with the following info: {}".format(
                    self.name, info
                )
            )
            logger.error(
                "You can delete it first using *database.delete_analyzer({})* and that create".format(
                    self.name
                )
            )
        except AnalyzerGetError:
            result = database.create_analyzer(
                self.name, self.type, self.get_properties(), self.features
            )
            logger.info("Analyzer was created!")
        return result


@dataclass
class AnalyzerList:
    analyzerList: List = field(default_factory=lambda: [])  # ["text_en"]
    database: StandardDatabase = None

    def get_invalid_analyzers(self, database: StandardDatabase, verbose=0):
        invalid_analyzer = []
        for analyzer in self.analyzerList:
            try:
                info = database.analyzer(analyzer)
                if verbose == 1:
                    logger.info(info)
            except AnalyzerGetError:
                invalid_analyzer.append(analyzer)
        return invalid_analyzer

    def filter_invalid_analyzers(
        self, database: StandardDatabase, verbose: int = 0
    ):
        invalid_analyzer = self.get_invalid_analyzers(database)
        if verbose == 1:
            if len(invalid_analyzer) > 0:
                logger.warning(
                    "Filtered out the following invalid analyzers: "
                    + str(invalid_analyzer)
                )
        self.analyzerList = [
            a for a in self.analyzerList if a not in invalid_analyzer
        ]

    def add_analyzer(self, analyzer_name: str, force_add=False):
        """
        Adds the analyzer name to a list. If force_add =True then it adds is even if this analyzer does not exist in the database
        """
        try:
            if self.database is not None:
                _ = self.database.analyzer(analyzer_name)
            else:
                print(
                    "couldnt validate analyzer because database connection is not set."
                )
            self.analyzerList.append(analyzer_name)
        except AnalyzerGetError:
            print("Invalid Analyzer")
            if force_add:
                self.analyzerList.append(analyzer_name)
