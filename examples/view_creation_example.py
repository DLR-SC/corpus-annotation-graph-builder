from arango import ArangoClient

from cag import logger
from cag.view_wrapper.arango_analyzer import ArangoAnalyzer, AnalyzerList
from cag.view_wrapper.link import Link, Field
from cag.view_wrapper.view import View


def run_sample(config):
    db = config.arango_db

    # Create analyzer
    analyzer = ArangoAnalyzer("analyzer_sample")
    analyzer.set_stopwords(
        language="english", custom_stopwords=["stop", "word"], include_default=False
    )
    analyzer.type = ArangoAnalyzer._TYPE_TEXT

    analyzer.create(db)

    # Create Link - a view can hvae 0 to * links
    link = Link(name="TextNode")  # Name of a collection in the database
    linkAnalyzers = AnalyzerList(["identity"])
    link.analyzers = linkAnalyzers

    # A link can have 0..* fields
    field = Field(
        "text", AnalyzerList(["text_en", "invalid_analyzer", "analyzer_sample"])
    )  # text_en is a predifined analyzer from arango
    logger.info(field.analyzers)
    field.analyzers.filter_invalid_analyzers(
        db, verbose=1
    )  # filters out the analyzer that are not defined in the database
    print("current analyzers after filtering invalid ones: ", field.analyzers)
    ## current analyzers after filtering invalid ones:  AnalyzerList(analyzerList=['text_en', 'analyzer_sample'])

    link.add_field(field)

    ## Show the dict format of all the fields in a link
    print(link.get_fields_dict())
    # {'text': {'analyzers': ['text_en', 'analyzer_sample']}}

    # create view
    view = View("sample_view", view_type="arangosearch")
    ## add the link (can have 0 or 1 link)
    view.add_link(link)

    ## can have 0..* primary sort
    view.add_primary_sort("text", asc=False)
    view.add_stored_value(["text", "timestamp"], compression="lz4")

    print("Prints the *view* as a dict:", view.summary())

    ## creates the view in the database
    view.create(db)
