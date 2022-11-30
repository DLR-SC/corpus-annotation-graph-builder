.. role:: python(code)
   :language: python


Get Started
===========

This package is based on the concept of using 3 stages for graph management:

1. Graph creation: :python:`GraphCreatorBase`: creates or updates a graph from a a datasource
2. Graph annotation: :python:`AnnotatorBase`: annotate (extend) graphs by running various algorithms over them
3. Graph anaylzers: :python:`AnalyzerBase`: run queries, analysis over graphs to gain insights and visualize the graph or parts of it.


Installation
------------

Using pip:


.. code-block:: bash

    pip install cag


First steps
-----------

Make sure you have an up-to-date ArangoDB instance running and can connect to it. You can connect to it using the :py:class:`cag.utils.config.Config` utilities:

.. code-block:: python


    from cag.utils.config import Config 
    conf = Config(database="YourDB", graph="KnowledgeGraph")

In order to connect, you have to have the graph created and imported somewhere (note: the relations defined here are not relevant, you have to define them in the Graph Creator):

.. code-block:: python


    from cag.graph_elements.base_graph import BaseGraph
    from pyArango.graph import Graph, EdgeDefinition

    class KnowledgeGraph(BaseGraph):
        _edgeDefinitions=[EdgeDefinition('GenericEdge', fromCollections=['GenericNode'], toCollections=['GenericNode'])] 
        _orphanedCollections = []

The next step is to create the graph creator and the graph definition. This basically defines your data model and how the nodes should be able to be connected, similar to an ER-model:

.. code-block:: python


    import cag.utils as utils
    from cag.framework import GraphCreatorBase
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
            corpus = self.create_corpus_node(key="AnyCorpus",
                                            name=AnyGraphCreator._name,
                                            type="journal",
                                            desc=AnyGraphCreator._description,
                                            created_on=datetime.datetime.today())
            # fetch your data, load it, etc,
            # self.corpus_file_or_dir can be used to tell your creator where your files or data is

Similar to the connection above, you need to have your collections present as a class due to the underlying connector system (pyArango). Furthermore, the only collections that will be created are the ones present in at least one edge definition.

Now you can instantiate your GraphCreator and run it:

.. code-block:: python

    gc = AnyGraphCreator('',conf,initialize=True)



