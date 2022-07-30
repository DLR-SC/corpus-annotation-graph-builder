
from pyArango.collection import Collection

from cag.graph_framework.components.annotators.pipeline import Pipeline


def run_sample(config):
    pipeline: Pipeline = Pipeline(database_config=config)
    # Pipeline.extend_config(extened_dict)

    pipeline.add_annotation_pipe("NamedEntityAnnotator", True)

    coll: Collection = pipeline.database_config.db["TextNode"]
    docs = coll.fetchAll(limit=500)
    processed = []
    for txt_node in docs:
        processed.append((txt_node.text, {"_key": txt_node._key}))
    pipeline.annotate(processed)

    pipeline.save()