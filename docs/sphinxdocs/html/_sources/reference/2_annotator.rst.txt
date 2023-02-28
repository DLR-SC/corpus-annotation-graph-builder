.. role:: python(code)
   :language: python


annotator
==========

Textmining annotator
--------------------


A simple pipeline, using existing pipes, can be created as follows (assuming you have an arangodb instance up and running):

.. code-block:: python


    from pyArango.collection import Collection

    from cag.framework.annotator.pipeline import Pipeline
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

General annotator
-----------------
These annotator fit a more general class, where we only provide basic functionality, similar to the graph creator. To ease the filtering based on the parameters, we provide a simple base class where the documents can be checked in and easily filtered:

.. code-block:: python

    from cag.framework import GenericAnnotator
    class AnyAnnotator(GenericAnnotator):
        def __init__(self, conf: Config, params={'mode': 'run-1'}, filter_annotatable=True):
            super().__init__(query=f"""FOR dp IN {AnyGraphCreator._ANY_DATASET_NODE_NAME}
            RETURN dp
            """, params=params, conf=conf, filter_annotatable=filter_annotatable)
        def update_graph(self, timestamp, data):
            for d in data:
                d['add-prop']=some_algo(d['text'])
                self.upsert_node(d) #will annotate the data!


You can disable the filtering by providing :python:`filter_annotatable=False`. When returning more complex data make sure that you also return a root-level field (in your data structure) called :python:`'_annotator_params'` (from a component that will be annotated) or provide your own fieldname in the parameter :python:`annotator_fieldname`. Each document that will be upserted (or checked into :python:`complete_annotation`) will recieve the parameter on this field, providing the next run with the neccessary information to filter.

An example for annotation metadata as a :python:`dict()` for annotations produced by keyphrase extraction is given below:

.. code-block:: python

    {
        "analysis_component": "keyphrase_extraction",
        "parameters": {
            "algorithm": "text_rank",
            "relevance_threshold": 0.75
        }
    }