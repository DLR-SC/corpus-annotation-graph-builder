import pandas as pd
from pyArango.document import Document
import pyArango
from cag.framework.annotator.element.orchestrator import PipeOrchestrator
from cag.framework.annotator.pipe.linguistic.emotion import (
    EmotionHartmannFactory,
)


class EmotionPipeOrchestrator(PipeOrchestrator):
    _EMOTIONS = [
        "anger",
        "disgust",
        "fear",
        "joy",
        "neutral",
        "sadness",
        "surprise",
    ]

    def create_node(self, emotion_label: str) -> pyArango.document.Document:
        data = {"label": emotion_label}
        return self.upsert_node(self.node_name, data, alt_key=["label"])

    def create_edge(
        self, _from: Document, _to: Document, emotion_attrs
    ) -> Document:
        return self.upsert_edge(self.edge_name, _from, _to, emotion_attrs)

    def save_annotations(self, annotated_texts: list) -> pd.DataFrame:
        out_arr = []
        for doc, context in annotated_texts:
            text_key = context["_key"]

            if doc._.emotions is not None and len(doc._.emotions) > 0:
                for emotion_score in doc._.emotions:
                    if emotion_score["count"] > 0:
                        emotion = emotion_score["label"]
                        entry = {}
                        entry["mean_score"] = emotion_score["mean_score"]
                        entry["count"] = emotion_score["count"]
                        entry["ratio"] = emotion_score["ratio"]

                        entry["is_dominant"] = (
                            True if doc._.emotion_label == emotion else False
                        )
                        entry[
                            "sentence_index_w_highest_score"
                        ] = emotion_score["sentence_index_w_highest_score"]

                        entry["highest_score"] = emotion_score["highest_score"]
                        entry["metadata"] = EmotionHartmannFactory._METADATA_
                        emotion_node: Document = self.create_node(emotion)
                        text_node: Document = self.get_document(
                            self.annotated_node, {"_key": text_key}
                        )
                        _ = self.create_edge(text_node, emotion_node, entry)

                        record = {
                            f"emotion_hartmann_{x}": y
                            for x, y in entry.items()
                        }
                        record["label"] = emotion
                        record["text_key"] = text_key

                        out_arr.append(record)
        out_df: pd.DataFrame = pd.DataFrame(out_arr)

        return out_df
