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

```python
from graph_framework.view_wrapper.arango_analyzer import ArangoAnalyzer

analyzer = ArangoAnalyzer("sample_analyzer")
analyzer.set_stopwords(language="english", custom_stopwords=['hello'], include_default=True)
analyzer.type = ArangoAnalyzer._TYPE_TEXT

analyzercreate(db)
```
## Usage

See sample projects for graph creation:
- [InsighstNet Graphs](https://gitlab.dlr.de/insightsnet/inisightsnet_code/-/tree/main/insightsnet_graphs)
- [PangeaKG]()

