.. role:: python(code)
   :language: python


Quick Start
===========

In the quick guide here, we show how to install CAG, create a sample graph from a datasource and extend the graph with annotation nodes.

0. Installation 
1. Graph creation: :python:`GraphCreatorBase`: creates or updates a graph from a  datasource
2. Graph annotation: :python:`AnnotatorBase`: annotate (extend) graphs by running various algorithms over them


.. _qs-installation:

Installation
------------

You can download `CAG using Pypi`_.

.. _CAG using Pypi: https://pypi.org/project/cag/


.. code-block:: bash

    pip install cag

Or, to install the latest fixes, you can install CAG from GitHub:

.. code-block:: bash
    
    pip install git+https://github.com/DLR-SC/corpus-annotation-graph-builder.git

.. _qs-build:

Build your First Graph
----------------------

Make sure you have an up-to-date ArangoDB instance running and can connect to it. You can connect to it using the :py:class:`cag.utils.config.Config` utilities:

.. code-block:: python


    from cag.utils.config import Config 
    conf = Config(database="YourDB", graph="KnowledgeGraph")


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



.. _qs-annotate:


Annotate your First Graph
--------------------------