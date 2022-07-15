# Corpus Analytics Graph

## Overview
Corpus Analytics Graph serves as a base framework to create an ArangoDB graphs and Arango [Views](https://www.arangodb.com/docs/stable/arangosearch-views.html). It contains basic *nodes* (aka Vertices in ArangoDB) and *Relations* (a.k.a Edges in ArangoDB).

## Installation

This package is in early developement stages - to use/update it, clone the repository, and go to the root folder and then run

```python
pip install -e .
```

This will allow you to use the module `graph_frameworks` from any python script locally.

## Documentation

### Graph creation
#TODO

### Arango Views

The arango view wrapper has classes that facilitates the creation of arango view and all its properties and components.

#### create an analyzer

The analyzer class, loads the required attributes of an analyzer based on its type. The supported types are:
* _TYPE_IDENTITY -> "identity", **attributes to set:** None
* _TYPE_TEXT -> "text", **attributes to set:** 'locale', 'case', 'stopwords', 'accent', 'stemming', 'edge_ngram'
* _TYPE_NGRAM -> "ngram", **attributes to set:**  'min', 'max', 'preserve_original', 'start_marker', 'end_marker', 'stem_type'
* _TYPE_STEM -> "stem", **attributes to set:** locale
* _TYPE_DELIMITE -> "delimiter", **attributes to set:** delimiter

```python
from graph_framework.view_wrapper.arango_analyzer import ArangoAnalyzer, EdgeNGram

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
client = ArangoClient()
database = client.db('_System', username='root', password='root')
analyzer.create(database)
```

#### create a view

## Usage

See sample projects for graph creation:
- [InsighstNet Graphs](https://gitlab.dlr.de/insightsnet/inisightsnet_code/-/tree/main/insightsnet_graphs)
- [PangeaKG]()

