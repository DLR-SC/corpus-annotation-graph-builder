
from cag.graph_framework.components import GenericAnnotator
from cag.graph_framework.components.annotators.pipeline.pipeline_base import Pipeline
from cag.utils.config import *

from examples.graph_creation_example import AnyGraphCreator
from pyArango.query import AQLQuery

from pyArango.collection import Collection

class AnyAnnotator(GenericAnnotator):
    def __init__(self, conf: Config, params={'mode': 'run-1'}, filter_annotatable=True):
        super().__init__(query=f"""FOR dp IN {AnyGraphCreator._ANY_DATASET_NODE_NAME}
        RETURN dp
        """, params=params, conf=conf, filter_annotatable=filter_annotatable, run=True)

    def update_graph(self, timestamp, data: AQLQuery):
        for dp in data:
            pass


## Pipeline for specialized annotator

class SamplePipeline(Pipeline):

     def process_input(self) -> list:
        processed = []
        for txt_node in self.input:
            processed.append((txt_node.text, {"_key": txt_node._key}))

        return processed

     def init_and_run(self):
        # Extend the Default toml if needed, by either defining the path of a dictionary
         # Pipeline.extend_config(extened_dict)

        # Add the pipes defined in the Toml files
         self.add_annotation_pipe(name = "NamedEntityAnnotator", save_output= True, is_spacy=True)
         self.add_annotation_pipe(name = "EmpathAnnotator", save_output= True, is_spacy=True)
         self.add_annotation_pipe(name = "DummyDefaultAnnotator", save_output= False, is_spacy=False)

        # Get your Input in any way you like
         coll: Collection = self.database_config.db["TextNode"]
         docs = coll.fetchAll(limit=50)

        # Set the INPUT - this will automatically call process_input (make sure to implement it
         self.set_input(docs)

        # annotate the input
         self.set_spacy_language_model("en_core_web_md")
         self.annotate()
        # save annotations when "save_output" is set to True
         self.save()

def run_sample(config):
    sample_pipeline = SamplePipeline(config)
    sample_pipeline.init_and_run()
