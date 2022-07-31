# Corpus Analytics Graph (CAG)

## Table of Content

[Overview](#overview)

[Installation](#install)

[Documentation](#documentation)

## Overview

<a name="overview"/>

Corpus Analytics Graph (CAG) serves as a base framework to create graphs, extend them and analyze them.

We use ArangoDB to store the graphs. This framework has three main components, located under `cag.graph_framework.components`:

- [Graph Creator -  `cag.graph_framework.components.graph_creators` ](#graph_creator)
    
- [Annotator `cag.graph_framework.components.annotators`](#annotator)

- [Analyzer - `cag.graph_framework.components.analyzers`](#analyzer)

cag also contains a tool to facilitate the creation of Arango Views:
- [View Wrapper - `cag.view_wrapper`](#arango_view)

    graph_framework:graphs and Arango [Views](https://www.arangodb.com/docs/stable/arangosearch-views.html). It contains basic *nodes* (aka Vertices in ArangoDB) and *Relations* (a.k.a Edges in ArangoDB).
## Installation
<a name="install"/>

### Manual cloning
This package is in early developement stages - to use/update it, clone the repository, and go to the root folder and then run

```
pip install .
```
### Direct install via pip 
The package can also be installed directly via pip
```
pip install git+https://gitlab.dlr.de/sc/ivs-open/corpus_analytics_graph
```

This will allow you to use the module **`cag`** from any python script locally. The two main packages are **`cag.graph_framework`** and **`cag.view_wrapper`**.

## Documentation
<a name="documentation"/>

### Graph Creator -  `cag.graph_framework.components.graph_creators`

<a name="graph_creator"/>

The graph_creator has the tools and infrastructure to allow the user to build, and maintain a graph with its defined nodes. This framework defines generic nodes and relations (a.k.a edges): [`cag.graph_framework.graph.nodes.py`](cag/graph_framework/graph/nodes.py) and [`cag.graph_framework.graph.nodes.py`](cag/graph_framework/graph/relations.py).

See sample projects for graph creation:
- [InsighstNet Graphs](https://gitlab.dlr.de/insightsnet/inisightsnet_code/-/tree/main/insightsnet_graphs)
- [Pangea KG](https://gitlab.dlr.de/sc/ivs-open/pangaea-kg)


### Annotator `cag.graph_framework.components.annotators`
<a name="annotator"/>

the annotator is responsible for adding levels of abstractions in order to create a linkable graph. More precisely, this component is responsible for taking a set of nodes (e.g. TextNodes), and apply a pipeline (e.g. text mining pipeline) to extract features on the level of a single node or a collection. These extracted features are then saved in an *annotation node*.

As a start we support the creation of a textmining pipeline that can be customized by the user. The package contains some samples of features extractions ([`cag.graph_framework.components.annotators.textmining_pipes`](cag/graph_framework/components/annotators/textmining_pipes)). 

A simple pipeline, using existing pipes, can be created as follow:

```python
from pyArango.collection import Collection

from cag.graph_framework.components.annotators.pipeline import Pipeline


pipeline: Pipeline = Pipeline(database_config=config)

pipeline.add_annotation_pipe("NamedEntityAnnotator", True)

coll: Collection = pipeline.database_config.db["TextNode"]
docs = coll.fetchAll(limit=500)
processed = []
for txt_node in docs:
    processed.append((txt_node.text, {"_key": txt_node._key}))
pipeline.annotate(processed)

pipeline.save()
```

### Analyzer - [`cag.graph_framework.components.analyzers`](cag/graph_framework/components/analyzers)
<a name="analyzer"/>
The analyzer component is responisble for extracting insights from the graph. These insights can be in the form of a visualization or a curated list of items, ranked and processed based on user queries.

#TODO

### Arango Views - **`cag.view_wrapper`**
<a name="arango_view"/>

The arango view rapper is a tool to simplify the creation of Arango Analyzers. This tool can be used by the *Analyzer* component we mentioned above. This wrapper has classes that facilitates the creation of arango view and all its properties and components.

The full example can be found in the [main.py](main.py)

#### Create an analyzer

([source](https://www.arangodb.com/docs/stable/analyzers.html)):
> The valid attributes/values for the properties are dependant on what type is used. For example, the delimiter type needs to know the desired delimiting character(s), whereas the text type takes a locale, stop-words and more.

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

<details><summary>OUTPUT - Click to expand</summary>

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

</details>

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
<details><summary>OUTPUT - Click to expand</summary>

    current analyzers after filtering invalid ones:  AnalyzerList(analyzerList=['text_en', 'analyzer_sample'])  
</details>

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

<details><summary>OUTPUT - Click to expand</summary>

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
</details>





