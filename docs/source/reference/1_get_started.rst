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

You can download  the **latest stable** version of CAG from `Pypi`_.

.. _Pypi: https://pypi.org/project/cag/


.. code-block:: bash

    pip install cag

Or, to install the latest fixes, you can install CAG from GitHub:

.. code-block:: bash
    
    pip install git+https://github.com/DLR-SC/corpus-annotation-graph-builder.git


.. _qs-requiremnent:

Requirement
------------

Make sure you have an ArangoDB instance up and running. You can connect to it using the :py:class:`cag.utils.config.Config` utilities as shown in the code block below. your `config` instance will be used later on when you initiated you `Graph Creator`.

.. code-block:: python


    import cag.utils.config as config

    my_config = config.Config(
        url="http://127.0.0.1:8529", # URL to your ArangoDB instance
        user="root", # ArangoDB username
        password="root", # ArangoDB password
        database="_system", # The database name - DB will be created if it does not already exist
        graph="MyCagGraph", # Ypur graph name - A new graph will be created if it does not already exist
    )


.. _qs-build:

Build your First Graph
----------------------

In this section we show a quick example on how to create your graph from a datasource using CAG. For a more deailed guide, refer to the `Graph-Creator Section`.



Your `GraphCreator` inherits from the class :py:class:`cag.framework.creator.base_creator.GraphCreatorBase` which is an abstract class; it enforces the implementation of two functions: one for initializing (`init_graph()`) the graph from a datasource and one for updating it (`init_graph()`). In jupyter notebook `here`_, we create a sample graph.

.. _here: https://github.com/DLR-SC/corpus-annotation-graph-builder/blob/main/examples/1_create_graph.ipynb


Each GraphCreator would look as follows:

.. code-block:: python
    
    from cag.framework.creator.base_creator import GraphCreatorBase


    class MyDatasourceXGraphCreator(GraphCreatorBase):

        _name = "DatasourceX"
        _description = "This is the description of my DatasourceX"

        # Here you define a sub-ontology of your graph 
        # - only the ontology related to your DatasourceX

        # 1. Define Nodes not created in CAG
            # TODO
        # 2. Define relations 
            # TODO

        def init_graph(self):
            
            # Loop over each entry of your dataset and an load it to the graph
            # use the following to insert a node or edge (respectively):
                #      GENERIC functions: `self.upsert_node(name, attrs_dict, alt_key)`,
                #                         `self.upsert_edge(relation_name,
                #                                           from_node, to_node, attrs_dict)`
                #      Specific functions: `self.create_author_node()`, `self.create_author_node()`
            
            pass

        def update_graph(self, timestamp):
            return self.init_graph()


.. _qs-annotate:


Annotate your First Graph
--------------------------

In `*annotation* jupyter notebook`_, we create an annotation pipeline and .

.. _*annotation* jupyter notebook: https://github.com/DLR-SC/corpus-annotation-graph-builder/blob/main/examples/2_annotate_graph.ipynb