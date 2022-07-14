from graph_framework.utils import utils


class EdgeNGram(object):

    def __init__(self, min = 2, max=4, preserve_original = False):
        self.min = min
        self.max = max
        self.preserve_original = preserve_original

    def summary(self):
        return vars(self)


class ArangoAnalyzer():
    ### CONBSTANTS - the main types of arango analyzer
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
        _TYPE_IDENTITY : _MANDATORY_FIELDS,
        _TYPE_TEXT: _MANDATORY_FIELDS + ['local', 'case', 'stopwords', 'accent', 'stemming', 'edge_n_gram'],
        _TYPE_NGRAM: _MANDATORY_FIELDS + ['min', 'max', 'preserve_original',
                                               'start_marker', 'end_marker', 'stem_type'],
        _TYPE_STEM: _MANDATORY_FIELDS + ['local'],
        _TYPE_DELIMITER: _MANDATORY_FIELDS + ['delimiter'],
    }

    def __init__(self, name= "sample_analyzer", type = _TYPE_IDENTITY):

        self.name = name
        self.type = type
        self.features = ["frequency", "norm", "position"]

        ## Properties - loaded based on type
        # TEXT
        self.local = "en" # text, stem, norm
        self.case = "lower" # text,  norm
        self.stopwords = []
        self.accent = False # text,  norm
        self.stemming = True
        self.edge_n_gram = EdgeNGram(min =2, max = 5, preserve_original = False)
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
        features = []
        if frequency: features.append("frequency")
        if norm: features.append("norm")
        if position: features.append("position")
        self.features = features

    def list_type_fields(self):
        return ArangoAnalyzer.FIELDS[self.type]

    def summary(self):
        keep = ArangoAnalyzer.FIELDS[self.type]
        dict_ = utils.to_dictionary(self)
        result ={k:v for k,v in dict_.items() if k in keep}
        #result ={k:vars(v) for k,v in dict_.items() if isinstance(v, EdgeNGram)}
        return result


## TEST REMOVE THIS TO ANOTHER PLACE
def main():
    aa = ArangoAnalyzer()
    print("\n################")
    print(aa.type)
    print(aa.list_type_fields())
    print(aa.summary())

    b = ArangoAnalyzer()
    b.type = ArangoAnalyzer._TYPE_TEXT
    print("\n################")

    print(b.type)
    print(b.list_type_fields())
    print(b.summary())

    deli = ArangoAnalyzer()
    deli.type = ArangoAnalyzer._TYPE_DELIMITER
    print("\n################")
    print(deli.type)
    print(deli.list_type_fields())
    print(deli.summary())

    ngram = ArangoAnalyzer()
    ngram.type = ArangoAnalyzer._TYPE_NGRAM
    print("\n################")
    print(ngram.type)
    print(ngram.list_type_fields())
    print(ngram.summary())

if __name__ == "__main__":
    main()