CAG Concepts
============



The graph is, both, object of analysis as well as result container. This means that annotation runs evaluate the graph and enrich it with annoations. 

In the example below object of study (OOS) nodes are depicted as white and blue boxes and annoation nodes as grey boxes. OOS nodes are created by :ref:`Graph Creators <graph-creators>` that read raw corpus data and map it to the OOS graph. Graph builders also create some basic self-evident annotations (e.g. methods, provided keywords, categories, etc.). The OOS nodes are analysed by automatic :ref:`annotator <annotator>`, which add or update annoations to the graph. 

.. image:: /imgs/cag.png


The enriched graph can be further analysed or queried by :ref:`Analyzers <analyzer>` for producing results to be presented to the end-users.

.. _graph-creators:

Graph Creators
--------------

The Graph Creators has the tools and infrastructure to allow the user to build and maintain a graph with its defined nodes. This framework defines some generic nodes and relations (a.k.a edges): :py:mod:`cag.graph_elements.nodes`  and :py:mod:`cag.graph_elements.relations` which should apply to most knowledge corpus.

Graph creator components evaluate raw corpus data and map it to the graph by creating OOS nodes and corresponding relations.

**Input:** Raw corpus data

**Output:** Object of study (OOS) nodes, self-evident annotations and relations in ArangoDB

**Metadata stored in nodes and edges:**

- Timestamp

You can learn about how to create one in the :doc:`get started guide <1_get_started>`

.. _annotator:

annotator
----------

Annotator components enrich the graph by analysing OOS nodes and edge them to newly created annotation nodes. Annotations can be on different levels. For example, corpus level (e.g. corpus statistics, topics), text nodes (e.g. named entities, keyphrases), image nodes (e.g. generated caption), etc.

**Input:** Knowledge Graph, Subgraph selection query

**Output:** Annotation nodes and relations in ArangoDB

**Metadata stored in annotation nodes and annotated edges:**

- Timestamp
- Component that created the annotation
- Parameters used for analysing content nodes

The annotator is responsible for adding levels of abstractions to create a edgeable graph. More precisely, this component is responsible for taking a set of nodes (e.g., TextNodes) and applying a pipeline (e.g., text mining pipeline) to extract features on the level of a single node or a collection. These extracted features are then saved in an *annotation node* or directly on the annotated node.

As a start, we support the creation of a text-mining pipeline that the user can customize. The package contains some samples of features extractions :py:mod:`cag.framework.annotator.textmining_pipes`.  Alternatively, we provide some functionality in a low-level extensible class, similar to the graph creator. You can read about how to use it in the :doc:`annotator guide <2_annotator>`




**Gradual update rules:**

The annotation metadata is used to keep the annoation graph consistent and to avoid unneccessary computations. 

An annotation of a OOS node is only computed once. To this end, before an annotator (parameterized by algorithm and settings) analyzes an OOS node, it first checks if there exists already an attached annotation node that has matching parameter settings in its metadata. In this way annotations can be created on demand for specific subgraphs depending on the analysis goal and re-used where possible. The more analysis runs performed, the less likely it is that a OOS node has to be evaluated.

However, since the corpus builder can modify the OOS part of the graph annotations may need to be updated after graph updates. The timestamp propagation mechanism of the graph builder components described above ensures that the timestamp of OOS nodes is updated if it was affected by a graph update. If the timestamp of an annotation is smaller than the timestamp of its attached OOS node, it might be outdated and needs re-computation.

Two options for annotation updates *(open issue)*:

1. Compute new delete old (Pro: No legacy information, Con: Graph is not fully reversible to a prior state).
2. Compute new flag old as outdated (Pro: Graph is fully reversible to any prior state, Con: Graph may contain much useless information, e.g. results from trial runs)

These are open to change, so please open an issue to discuss how this system should handle these updates in the future!

.. _analyzer:

Analyzers
---------
The analyzer component is responsible for extracting insights from the graph. These insights can be in the form of visualization or a curated list of items ranked and processed based on user queries. Some analysers may simply read out information from the graph (e.g. corpus topics) and create a representation for the end user. Others can perform analyses based on specific queries (e.g. determining collocates of a given query term).

**Input:** Updated Knowledge Graph, Subgraph selection query

**Output:** Analysis results and visualisations
 
You can read more on how to use them in the :doc:`analyzer guide <3_analyzer>`
