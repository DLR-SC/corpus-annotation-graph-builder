from pyArango.document import Document
from cag.framework.annotator.element.orchestrator import PipeOrchestrator
import pandas as pd


class MediaTopicPipeOrchestrator(PipeOrchestrator):
    def create_node(self, mediatopic_id, name) -> Document:
        data = {"mediatopic_id": mediatopic_id,
                "name": name}
        return self.upsert_node(self.node_name,
                                data,
                                alt_key=["mediatopic_id", "name"])

    def create_edge(self, from_: Document, to_: Document, entry) -> Document:
        return self.upsert_edge(self.edge_name, from_, to_, edge_attrs=entry)

    def save_annotations(self, annotated_texts: "[]"):
        out_arr = []
        for doc, context in annotated_texts:
            text_key = context["_key"]

            for level, media_topics in doc._.media_topic.items():
                
                media_topic_node: Document = self.create_node(media_topics[0],
                                                              media_topics[1])
                text_node: Document = self.get_document(
                    self.annotated_node, {"_key": text_key}
                )

                entry = {
                    "level": level,
                }

                _: Document = self.create_edge(
                    text_node, media_topic_node, entry
                )

                record = {f"mediatopic_{x}": y for x, y in entry.items()}
                record["mediatopic_id"] = media_topic_node[0]
                record["mediatopic_name"] = media_topic_node[1]
                record["text_key"] = text_key
                out_arr.append(record)
        out_df: pd.DataFrame = pd.DataFrame(out_arr)

        return out_df
