from arango import ArangoClient

from cag import logger
from cag.view_wrapper.arango_analyzer import ArangoAnalyzer, AnalyzerList
from cag.view_wrapper.link import Link, Field
from cag.view_wrapper.view import View


def sample():
    client = ArangoClient()

    # Connect to the database as root user.
    db = client.db('InsightsNet', username='root', password='root')

    # Create analyzer
    analyzer = ArangoAnalyzer("analyzer_sample")
    analyzer.set_stopwords(language="english", custom_stopwords=['stop', 'word'], include_default=False)
    analyzer.type = ArangoAnalyzer._TYPE_TEXT

    analyzer.create(db)

    # Create Link - a view can hvae 0 to * links
    link = Link(name="TextNode")  # Name of a collection in the database
    linkAnalyzers = AnalyzerList(["identity"])
    link.analyzers = linkAnalyzers

    # A link can have 0..* fields
    field = Field("text", AnalyzerList(
        ["text_en", "invalid_analyzer", "analyzer_sample"]))  # text_en is a predifined analyzer from arango
    logger.info(field.analyzers)
    field.analyzers.filter_invalid_analyzers(db,
                                             verbose=1)  # filters out the analyzer that are not defined in the database
    print("current analyzers after filtering invalid ones: ", field.analyzers)
    ## current analyzers after filtering invalid ones:  AnalyzerList(analyzerList=['text_en', 'analyzer_sample'])

    link.add_field(field)

    ## Show the dict format of all the fields in a link
    print(link.get_fields_dict())
    # {'text': {'analyzers': ['text_en', 'analyzer_sample']}}

    # create view
    view = View('sample_view',
                view_type="arangosearch")
    ## add the link (can have 0 or 1 link)
    view.add_link(link)

    ## can have 0..* primary sort
    view.add_primary_sort("text", asc=False)
    view.add_stored_value(["text", "timestamp"], compression="lz4")

    print("Prints the *view* as a dict:", view.summary())
    """

    Prints
    the * view * as a dict: 
    {'name': 'sample_view', 'viewType': 'arangosearch',
           'properties': {'cleanupintervalstep': 0, 'cleanupIntervalStep': 0, 'commitIntervalMsec': 1000,
                          'consolidationIntervalMsec': 0,
                          'consolidationPolicy': {'type': 'tier', 'segmentsMin': 1, 'segmentsMax': 10,
                                                  'segmentsBytesMax': 5368709120, 'segmentsBytesFloor': 2097152,
                                                  'minScore': 0}, 'primarySortCompression': 'lz4',
                          'writebufferIdle': 64, 'writebufferActive': 0, 'writebufferMaxSize': 33554432}, 'links': {
            'TextNode': {'analyzers': ['identity'], 'fields': {'text': {'analyzers': ['text_en', 'analyzer_sample']}},
                         'includeAllFields': False, 'trackListPositions': False, 'inBackground': False}},
           'primarySort': [{'field': 'text', 'asc': False}],
           'storedValues': [{'fields': ['text'], 'compression': 'lz4'},
                            {'fields': ['timestamp'], 'compression': 'lz4'}]}
    """

    ## creates the view in the database
    view.create(db)


