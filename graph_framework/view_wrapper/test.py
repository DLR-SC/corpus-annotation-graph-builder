## TEST REMOVE THIS TO ANOTHER PLACE
import logging

from arango import ArangoClient

from graph_framework.view_wrapper.arango_analyzer import ArangoAnalyzer, AnalyzerList
from graph_framework.view_wrapper.link import Link, Field
from graph_framework.view_wrapper.view import View


def main():
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('InsightsNet', username='root', password='p3yqy8I0dHkpOrZs')

    b = ArangoAnalyzer("TheText_STOP_new")
    b.set_stopwords(language="english", custom_stopwords=['added', 'YOUPPPPPYYY'], include_default=True)
    b.type = ArangoAnalyzer._TYPE_TEXT

    b.create(db)

    #print(db.analyzer('TheText_STOP_newas'))

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