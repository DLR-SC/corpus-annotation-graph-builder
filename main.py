from pyArango.collection import Collection

import  examples.view_creation_example
import examples.graph_creation_example
import examples.annotation_example
from cag.graph_framework.components.annotators.elements.ner_annotator import NamedEntityAnnotator
from cag.graph_framework.components.annotators.pipeline import Pipeline
from cag.utils.config import Config

def main():
    config= Config(
        url="http://127.0.0.1:8529",
        user="root",
        password="root",
        database="_system",
        graph="GenericGraph"
    )

    examples.annotation_example.run_sample(config)



if __name__ == "__main__":
    main()