import logging

from cag.view_wrapper.arango_analyzer import ArangoAnalyzer, AnalyzerList
from cag.view_wrapper.link import Link, Field
from cag.view_wrapper.view import View
from tests import config_factory


class TestView:
    def test_creation(self):
        """
        Test creating an ArangoDB analyzer using the ArangoAnalyzer class.

        This test creates an analyzer object with custom settings, sets its attributes,
        and creates it in the ArangoDB database using the `create()` method. It then asserts
        that the analyzer object's attributes are correctly set and that the analyzer is
        created in the database by checking for its existence.

        Raises:
            AssertionError: if the created analyzer's attributes are not as expected or if
                            the analyzer does not exist in the ArangoDB database.
        """
        config = config_factory()
        db = config.arango_db

        # Create analyzer
        analyzer = ArangoAnalyzer("analyzer_sample")
        analyzer.set_stopwords(
            language="english",
            custom_stopwords=["stop", "word"],
            include_default=False,
        )
        analyzer.type = ArangoAnalyzer._TYPE_TEXT

        analyzer.create(db)
        assert analyzer.__dict__ == {
            "name": "analyzer_sample",
            "type": "text",
            "features": ["frequency", "norm", "position"],
            "locale": "en",
            "case": "lower",
            "stopwords": ["stop", "word"],
            "accent": False,
            "stemming": True,
            "edge_ngram": None,
            "delimiter": ",",
            "min": 2,
            "max": 5,
            "preserve_original": False,
            "start_marker": "",
            "end_marker": "",
            "stem_type": "binary",
        }
        assert isinstance(db.analyzer("analyzer_sample"), dict)

    def test_duplicate_creation(self, caplog):
        """
        Test creating a duplicate ArangoDB analyzer using the ArangoAnalyzer class.

        This test creates an analyzer object with custom settings and creates it in the ArangoDB
        database using the `create()` method. It then creates a second analyzer object with the same
        name and settings and attempts to create it in the database. The test asserts that the second
        creation attempt fails with an error message logged to the console indicating that an analyzer
        with the same name already exists in the database.

        Args:
            caplog: pytest fixture to capture log output.

        Raises:
            AssertionError: if the duplicate analyzer creation attempt does not fail or if the error
                            message logged to the console is not as expected.
        """
        config = config_factory()
        db = config.arango_db

        # Create analyzer
        analyzer = ArangoAnalyzer("analyzer_sample")
        analyzer.set_stopwords(
            language="english",
            custom_stopwords=["stop", "word"],
            include_default=False,
        )
        analyzer.type = ArangoAnalyzer._TYPE_TEXT

        analyzer.create(db)
        assert analyzer.__dict__ == {
            "name": "analyzer_sample",
            "type": "text",
            "features": ["frequency", "norm", "position"],
            "locale": "en",
            "case": "lower",
            "stopwords": ["stop", "word"],
            "accent": False,
            "stemming": True,
            "edge_ngram": None,
            "delimiter": ",",
            "min": 2,
            "max": 5,
            "preserve_original": False,
            "start_marker": "",
            "end_marker": "",
            "stem_type": "binary",
        }
        assert isinstance(db.analyzer("analyzer_sample"), dict)
        # Create analyzer
        analyzer = ArangoAnalyzer("analyzer_sample")
        analyzer.set_stopwords(
            language="english",
            custom_stopwords=["stop", "word"],
            include_default=False,
        )
        analyzer.type = ArangoAnalyzer._TYPE_TEXT

        analyzer.create(db)
        assert (
            "You can delete it first using *database.delete_analyzer(analyzer_sample)*"
            in caplog.text
        )

    def test_create_view(self):
        """
        Test function to create an ArangoSearch view in a given ArangoDB database.

        The test first creates an analyzer and a link with a field that uses this analyzer.
        Then, it creates a view with the link and defines primary sort and stored values.
        The summary of the view is checked against the expected output.
        Finally, the view is created in the database and its name is checked.

        Raises:
            AssertionError: if any of the assertions fail

        Returns:
            None
        """
        config = config_factory()
        db = config.arango_db

        # Create analyzer
        analyzer = ArangoAnalyzer("analyzer_sample")
        analyzer.set_stopwords(
            language="english",
            custom_stopwords=["stop", "word"],
            include_default=False,
        )
        analyzer.type = ArangoAnalyzer._TYPE_TEXT

        analyzer.create(db)

        # Create Link - a view can hvae 0 to * links
        link = Link(name="TextNode")  # Name of a collection in the database
        linkAnalyzers = AnalyzerList(["identity"])
        link.analyzers = linkAnalyzers

        # A link can have 0..* fields
        field = Field(
            "text",
            AnalyzerList(["text_en", "invalid_analyzer", "analyzer_sample"]),
        )  # text_en is a predifined analyzer from arango
        field.analyzers.filter_invalid_analyzers(
            db, verbose=1
        )  # filters out the analyzer that are not defined in the database

        assert (
            str(field.analyzers)
            == "AnalyzerList(analyzerList=['text_en', 'analyzer_sample'], database=None)"
        )

        link.add_field(field)

        ## Show the dict format of all the fields in a link
        assert link.get_fields_dict() == {
            "text": {"analyzers": ["text_en", "analyzer_sample"]}
        }

        # create view
        view = View("sample_view", view_type="arangosearch")
        ## add the link (can have 0 or 1 link)
        view.add_link(link)

        ## can have 0..* primary sort
        view.add_primary_sort("text", asc=False)
        view.add_stored_value(["text", "timestamp"], compression="lz4")

        assert view.summary() == {
            "name": "sample_view",
            "viewType": "arangosearch",
            "properties": {
                "cleanupintervalstep": 0,
                "cleanupIntervalStep": 0,
                "commitIntervalMsec": 1000,
                "consolidationIntervalMsec": 0,
                "consolidationPolicy": {
                    "type": "tier",
                    "segmentsMin": 1,
                    "segmentsMax": 10,
                    "segmentsBytesMax": 5368709120,
                    "segmentsBytesFloor": 2097152,
                    "minScore": 0,
                },
                "primarySortCompression": "lz4",
                "writebufferIdle": 64,
                "writebufferActive": 0,
                "writebufferMaxSize": 33554432,
            },
            "links": {
                "TextNode": {
                    "analyzers": ["identity"],
                    "fields": {
                        "text": {"analyzers": ["text_en", "analyzer_sample"]}
                    },
                    "includeAllFields": False,
                    "trackListPositions": False,
                    "inBackground": False,
                }
            },
            "primarySort": [{"field": "text", "asc": False}],
            "storedValues": [
                {"fields": ["text"], "compression": "lz4"},
                {"fields": ["timestamp"], "compression": "lz4"},
            ],
        }

        ## creates the view in the database
        view.create(db)

        assert db.view("sample_view")["name"] == "sample_view"