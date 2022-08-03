# Corpus Analytics Graph (CAG)

## Table of Content

[Overview](#overview)

[Installation](#install)

[Documentation](#documentation)
  - [Graph Creator -  `cag.graph_framework.components.graph_creators` ](#graph_creator)
    
  - [Annotator `cag.graph_framework.components.annotators`](#annotator)

  - [Analyzer - `cag.graph_framework.components.analyzers`](#analyzer)

  - [Tool to create views - View Wrapper - `cag.view_wrapper`](#arango_view)

## Overview

<a name="overview"/>

Corpus Analytics Graph (CAG) serves as a base framework for creating graphs, extending them, and analyzing them.

We use ArangoDB to store the graphs. This framework has three main components, located under `cag.graph_framework.components`:

- [Graph Creator -  `cag.graph_framework.components.graph_creators` ](#graph_creator)
    
- [Annotator `cag.graph_framework.components.annotators`](#annotator)

- [Analyzer - `cag.graph_framework.components.analyzers`](#analyzer)

cag also contains a tool to facilitate the creation of Arango [views](https://www.arangodb.com/docs/stable/arangosearch-views.html):
- [View Wrapper - `cag.view_wrapper`](#arango_view)


## Installation

<a name="install"/>

### Manual cloning
This package is in the early development stages - to use/update it, clone the repository, go to the root folder and then run:

```
pip install .
```
### Direct install via pip 
The package can also be installed directly via pip.
```
pip install git+https://gitlab.dlr.de/sc/ivs-open/corpus_analytics_graph
```

This will allow you to use the module **`cag`** from any python script locally. The two main packages are **`cag.graph_framework`** and **`cag.view_wrapper`**.


## Concept

The graph is, both, object of analysis as well as result container. This means that annotation runs evaluate the graph and enrich it with annoations. 

In the example below object of study (OOS) nodes are depicted as white and blue boxes and annoation nodes as grey boxes. OOS nodes are created by [Graph Creators](#graph-creators) that read raw corpus data and map it to the OOS graph. Graph builders also create some basic self-evident annotations (e.g. methods, provided keywords, categories, etc.). The OOS nodes are analysed by automatic [Annotators](#annotators), which add or update annoations to the graph. 


![OOS Grapg](img/OoS_Data_Model.drawio.png)

In order to create direct links between annotations [Annotation Linkers](#annotation-linkers) establish relations between existing annotations like "is identical to", "belongs to", etc. 

The enriched InsightsNet graph can be further analysed or queried by [Analyzers](#analyzers) for producing results to be presented to the end-users.


## Documentation
<a name="documentation"/>

### Graph Creator -  `cag.graph_framework.components.graph_creators`

<a name="graph_creator"/>

The graph_creator has the tools and infrastructure to allow the user to build and maintain a graph with its defined nodes. This framework defines generic nodes and relations (a.k.a edges): [`cag.graph_framework.graph.nodes.py`](cag/graph_framework/graph/nodes.py) and [`cag.graph_framework.graph.relations.py`](cag/graph_framework/graph/relations.py).

See sample projects for graph creation:
- [InsighstNet Graphs](https://gitlab.dlr.de/insightsnet/inisightsnet_code/-/tree/main/insightsnet_graphs)
- [Pangea KG](https://gitlab.dlr.de/sc/ivs-open/pangaea-kg)

Graph creator components evaluate raw corpus data and map it to the graph by creating OOS nodes and corresponding relations.

**Input:** Raw corpus data

**Output:** Object of study (OOS) nodes, self-evident annotations and relations in ArangoDB

**Metadata stored in nodes and edges:**

- Timestamp

A simple example can be found in [the examples folder](examples/graph_creation_example.py). The basic idea is to extend the `GraphCreatorBase` where you can access all the relevant helpers methods and which will, upon instantion, create your defined graph (including all relevant collections and edges - you have to include each collection to create in at leat one edge definition):

```python
import cag.utils as utils
from cag.graph_framework.components import GraphCreatorBase
import datetime
class AnyGraphCreator(GraphCreatorBase):
    _ANY_DATASET_NODE_NAME = "AnyDataset"
    _ANY_EDGE_PUB_CORPUS = "AnyEdgeDSCorpus"
    _name = "Any Graph Creator"
    _description = "Creates a graph based on any corpus"
    _edge_definitions = [
        {
            'relation': _ANY_EDGE_PUB_CORPUS,
            'from_collections': [_ANY_DATASET_NODE_NAME],
            'to_collections': [GraphCreatorBase._CORPUS_NODE_NAME]
        }
    ]


    def __init__(self, corpus_dir, config, initialize=False):
        super().__init__(corpus_dir, config, initialize)
    def init_graph(self):
        corpus = self.create_corpus_vertex(key="AnyCorpus",
                                           name=AnyGraphCreator._name,
                                           type="journal",
                                           desc=AnyGraphCreator._description,
                                           created_on=datetime.datetime.today())
        # fetch your data, load it, etc,
        # self.corpus_file_or_dir can be used to tell your creator where your files or data is

```

### Annotator `cag.graph_framework.components.annotators`
<a name="annotator"/>

Annotator components enrich the graph by analysing OOS nodes and link them to newly created annotation nodes. Annotations can be on different levels. For example, corpus level (e.g. corpus statistics, topics), text nodes (e.g. named entities, keyphrases), image nodes (e.g. generated caption), etc.

**Input:** Knowledge Graph, Subgraph selection query

**Output:** Annotation nodes and relations in ArangoDB

**Metadata stored in annotation nodes and annotated edges:**

- Timestamp
- Component that created the annotation
- Parameters used for analysing content nodes

The annotator is responsible for adding levels of abstractions to create a linkable graph. More precisely, this component is responsible for taking a set of nodes (e.g., TextNodes) and applying a pipeline (e.g., text mining pipeline) to extract features on the level of a single node or a collection. These extracted features are then saved in an *annotation node*.

As a start, we support the creation of a text-mining pipeline that the user can customize. The package contains some samples of features extractions ([`cag.graph_framework.components.annotators.textmining_pipes`](cag/graph_framework/components/annotators/textmining_pipes)). 

A simple pipeline, using existing pipes, can be created as follows (assuming you have an arangodb instance up and running) (see code [here](examples/annotation_example.py)):

```python
from pyArango.collection import Collection

from cag.graph_framework.components.annotators.pipeline import Pipeline
from cag.utils.config import Config

## set database configuration
config= Config(
        url="http://127.0.0.1:8529",
        user="root",
        password="root",
        database="_system",
        graph="GenericGraph"
    )

## define the pipeline
pipeline: Pipeline = Pipeline(database_config=config)

pipeline.add_annotation_pipe("NamedEntityAnnotator", save=True)

coll: Collection = pipeline.database_config.db["TextNode"]

## fetch data 
docs = coll.fetchAll(limit=500)
processed = []
for txt_node in docs:
    processed.append((txt_node.text, {"_key": txt_node._key}))

## annotating using the defined pipes
pipeline.annotate(processed)

## save to the database
pipeline.save()

```
NOTE: as a start, we support only text-based annotations. We will support other annotation types in the future.



** TODO: Gradual update rules (not yet implemented):**

The annotation metadata is used to keep the annoation graph consistent and to avoid unneccessary computations. 

An annotation of a OOS node is only computed once. To this end, before an annotator (parameterized by algorithm and settings) analyzes an OOS node, it first checks if there exists already an attached annotation node that has matching parameter settings in its metadata. In this way annotations can be created on demand for specific subgraphs depending on the analysis goal and re-used where possible. The more analysis runs performed, the less likely it is that a OOS node has to be evaluated.

However, since the corpus builder can modify the OOS part of the graph annotations may need to be updated after graph updates. The timestamp propagation mechanism of the graph builder components described above ensures that the timestamp of OOS nodes is updated if it was affected by a graph update. If the timestamp of an annotation is smaller than the timestamp of its attached OOS node, it might be outdated and needs re-computation.

Two options for annotation updates *(open issue)*:

1. Compute new delete old (Pro: No legacy information, Con: Graph is not fully reversible to a prior state).
2. Compute new flag old as outdated (Pro: Graph is fully reversible to any prior state, Con: Graph may contain much useless information, e.g. results from trial runs)

### Annotation Linkers

Annotation linkers (a.k.a edges)

**Input:** Knowledge Graph, Subgraph selection query

**Output:** Links between annoations in ArangoDB

**Metadata links between annotation:**

- Timestamp

To ease the filtering based on the parameters, we provide a simple base class where the documents can be checked in and easily filtered:

```python
from cag.graph_framework.components import AnnotatorBase
class AnyAnnotator(AnnotatorBase):
    def __init__(self, conf: Config, params={'mode': 'run-1'}, filter_annotatable=True):
        super().__init__(query=f"""FOR dp IN {AnyGraphCreator._ANY_DATASET_NODE_NAME}
        RETURN dp
        """, params=params, conf=conf, filter_annotatable=filter_annotatable)
    def update_graph(self, timestamp, data):
        for d in data:
            d['add-prop']=some_algo(d['text'])
            self.upsert_vert(d) #will annotate the data!
```
You can disable the filtering by providing `filter_annotatable=False`. When returning more complex data make sure that you also return a root-level field (in your data structure) called `_annotator_params` (from a component that will be annotated) or provide your own fieldname in the parameter `annotator_fieldname`. Each document that will be upserted (or checked into `complete_annotation`) will recieve the parameter on this field, providing the next run with the neccessary information to filter.

An example for annotation metadata in json format for annotations produced by keyphrase extraction is given below:

```json
{
    "analysis_component": "keyphrase_extraction",
    "parameters": {
        "algorithm": "text_rank",
        "relevance_threshold": 0.75
    }
}
```



### Analyzer - [`cag.graph_framework.components.analyzers`](cag/graph_framework/components/analyzers)
<a name="analyzer"/>
The analyzer component is responsible for extracting insights from the graph. These insights can be in the form of visualization or a curated list of items ranked and processed based on user queries. Some analysers may simply read out information from the graph (e.g. corpus topics) and create a representation for the end user. Others can perform analyses based on specific queries (e.g. determining collocates of a given query term).

**Input:** Updated Knowledge Graph, Subgraph selection query

**Output:** Analysis results and visualisations
 

Our analyzer allow you to easily write converters and graph visualizations. THe following sample allows you to see the connection between two corpus within one knowledge graph, convert that result to a `NetworkX` graph and visualize it using `pyvis` using little code outside the actual arango query:
```python
class CorpusDistanceAnalyzer(AnalyzerBase):
    def __init__(self, conf: Config):
        super().__init__(conf, run=False)

    def run(self, f_id, t_id):
        query = """FOR c_1 IN Corpus
    FILTER c_1._key==@f_id
    FOR c_2 IN Corpus
        FILTER c_2._key==@t_id
            FOR path IN ANY K_SHORTEST_PATHS c_1 TO c_2 GRAPH KnowledgeGraph
                LIMIT 100
                RETURN path"""
        aql = self.database.AQLQuery(query, bindVars={
            'f_id': f_id, 't_id': t_id}, rawResults=True)
        data = list(aql)
        g=self.visualize_graph(data)
        g.show() #if you are in a Jupyter Notebook
```


### Arango Views - **`cag.view_wrapper`**
<a name="arango_view"/>

The arango view wrapper is a tool to simplify the creation of Arango Analyzers. This tool can be used by the *Analyzer* component mentioned above. This wrapper has classes that facilitate the creation of arango view and all its properties and components.

The full example can be found [here](examples/view_creation_example.py)

#### Create an arango analyzer

([source](https://www.arangodb.com/docs/stable/analyzers.html)):
> The valid attributes/values for the properties depend on the type used. For example, the delimiter type needs to know the desired delimiting character(s), whereas the text type takes a locale, stop-words, and more.

The analyzer class loads the required attributes of an analyzer based on its type. The supported types are:
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
            "Frequency",
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

The analyzer can simply be created as follows:

```python

## Create 
from arango import ArangoClient

client = ArangoClient()
database = client.db('_System', username='root', password='root')
analyzer.create(database)
```

#### Create a *link* with *fields*

```python
    # Create Link - a view can have 0 to * links
    link = Link(name="TextNode") # Name of a collection in the database
    linkAnalyzers = AnalyzerList(["identity"])
    link.analyzers = linkAnalyzers

    # A link can have 0..* fields
    # for the *text* field in the *textNode* collection, add the analyzers below
    field = Field("text", AnalyzerList(["text_en", "invalid_analyzer", "analyzer_sample"])) # text_en is a predefined analyzer from arango
    
    # filters out the analyzer that are not defined in the database
    field.analyzers.filter_invalid_analyzers(DB, verbose=1) 
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
!!! Note: The links might need a few minutes to be created and to show in ArangoDB.

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
