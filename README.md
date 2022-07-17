# Corpus Analytics Graph

## Overview
Corpus Analytics Graph serves as a base framework to create an ArangoDB graphs and Arango [Views](https://www.arangodb.com/docs/stable/arangosearch-views.html). It contains basic *nodes* (aka Vertices in ArangoDB) and *Relations* (a.k.a Edges in ArangoDB).

## Installation

This package is in early developement stages - to use/update it, clone the repository, and go to the root folder and then run

```
pip install -e .
```

This will allow you to use the module `graph_frameworks` from any python script locally.

## Documentation

### Graph creation
#TODO

### Arango Views

The arango view wrapper has classes that facilitates the creation of arango view and all its properties and components.

The ful example can be found in the [main.py](main.py)
#### Create an analyzer

The analyzer class, loads the required attributes of an analyzer based on its type. The supported types are:
* _TYPE_IDENTITY -> "identity", **attributes to set:** None
* _TYPE_TEXT -> "text", **attributes to set:** 'locale', 'case', 'stopwords', 'accent', 'stemming', 'edge_ngram'
* _TYPE_NGRAM -> "ngram", **attributes to set:**  'min', 'max', 'preserve_original', 'start_marker', 'end_marker', 'stem_type'
* _TYPE_STEM -> "stem", **attributes to set:** locale
* _TYPE_DELIMITE -> "delimiter", **attributes to set:** delimiter

```python
from cag.view_wrapper.arango_analyzer import ArangoAnalyzer, EdgeNGram

analyzer = ArangoAnalyzer("sample_analyzer")
analyzer.type = ArangoAnalyzer._TYPE_TEXT
analyzer.set_stopwords(language="english", custom_stopwords=['hello'], include_default=False)

print(analyzer.get_type_fields())
## Returns: ['locale', 'case', 'stopwords', 'accent', 'stemming', 'edge_ngram']

analyzer.set_features(frequency=True, norm=True, position=True) # by defaults, all the features are set to True
analyzer.set_edge_ngrams(EdgeNGram(min=2,
                            max=4,
                            preserve_original=False))
print(analyzer.summary())
```
The summary returns the dictionary used to create the Analyzer:

```python
OUTPUT:
{
    "name": "sample_analyzer",
    "type": "text",
    "features": [
        "frequency",
        "norm",
        "position"
    ],
    "locale": "en",
    "case": "lower",
    "stopwords": [
        "hello"
    ],
    "accent": False,
    "stemming": True,
    "edgeNgram": {
        "min": {
            "min": 2,
            "max": 4,
            "preserveOriginal": False
        },
        "max": 5,
        "preserveOriginal": False
    }
}
```

The the analyzer can simply be created:

```python

## Create 
from arango import ArangoClient

client = ArangoClient()
database = client.db('_System', username='root', password='root')
analyzer.create(database)
```

#### Create a *link* with *fields*

```python
    # Create Link - a view can hvae 0 to * links
    link = Link(name="TextNode") # Name of a collection in the database
    linkAnalyzers = AnalyzerList(["identity"])
    link.analyzers = linkAnalyzers

    # A link can have 0..* fields
    # for the *text* field in the *textNode* collection, add the analyzers below
    field = Field("text", AnalyzerList(["text_en", "invalid_analyzer", "analyzer_sample"])) # text_en is a predifined analyzer from arango
    
    # filters out the analyzer that are not defined in the database
    field.analyzers.filter_invalid_analyzers(db, verbose=1) 
    print("current analyzers after filtering invalid ones: ", field.analyzers)
```

        OUTPUT: current analyzers after filtering invalid ones:  AnalyzerList(analyzerList=['text_en', 'analyzer_sample'])

```python
    link.add_field(field)

    ## Show the dict format of all the fields in a link
    print(link.get_fields_dict())
   

```


        OUTPUT: {'text': {'analyzers': ['text_en', 'analyzer_sample']}}

#### Create the *View*

```python

    view = View('sample_view',
                view_type="arangosearch")
    ## add the link (can have 0 or 1 link)
    view.add_link(link)

    ## can have 0..* primary sort
    view.add_primary_sort("text", asc = False)
    view.add_stored_value(["text", "timestamp"], compression="lz4")

    print("Prints the *view* as a dict:", view.summary())

```
!!! Note: The links might need few minutes to be created and to show in ArangoDB.

```
OUTPUT:
    {
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
            "minScore": 0
        },
        "primarySortCompression": "lz4",
        "writebufferIdle": 64,
        "writebufferActive": 0,
        "writebufferMaxSize": 33554432
    },
    "links": {
        "TextNode": {
            "analyzers": [
                "identity"
            ],
            "fields": {
                "text": {
                    "analyzers": [
                        "text_en",
                        "analyzer_sample"
                    ]
                }
            },
            "includeAllFields": False,
            "trackListPositions": False,
            "inBackground": False
        }
    },
    "primarySort": [
        {
            "field": "text",
            "asc": False
        }
    ],
    "storedValues": [
        {
            "fields": [
                "text"
            ],
            "compression": "lz4"
        },
        {
            "fields": [
                "timestamp"
            ],
            "compression": "lz4"
        }
    ]
}
```
## Graph Usage

See sample projects for graph creation:
- [InsighstNet Graphs](https://gitlab.dlr.de/insightsnet/inisightsnet_code/-/tree/main/insightsnet_graphs)
- [Pangea KG]()

