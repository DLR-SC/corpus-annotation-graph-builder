
from typing import ClassVar, List
import pandas as pd
from pyArango.document import Document
import pyArango
from cag.utils.config import Config
from cag.framework.annotator.element.orchestrator import PipeOrchestrator


class EmotionPipeOrchestrator(PipeOrchestrator):
    _EMOTIONS = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]

    def create_node(self, emotion_label:str) -> pyArango.document.Document:
        data = {"label": emotion_label}
        return self.upsert_node(self.node_name, data, alt_key=["label"])

    def create_edge(self, _from: Document, _to: Document, emotion_attrs) -> Document:
        
        #edge_dict: dict = self.get_edge_attributes(self.edge_name, _from, _to)
        #edge = self.get_document(self.edge_name, edge_dict)

        return self.upsert_edge(self.edge_name, _from, _to, emotion_attrs )


    def save_annotations(self, annotated_texts: list) -> pd.DataFrame:

        out_arr = []
        for doc, context in annotated_texts:
            text_key = context["_key"]

            entry = {self.input_id: context[self.input_id]}

            if doc._.emotions is not None and len(doc._.emotions)>0:
                for emotion_score in doc._.emotions:
                    entry[f"emotion_hartmann_{emotion_score['label']}_mean"] = emotion_score['score_mean']
                    entry[f"emotion_hartmann_{emotion_score['label']}_count"] = emotion_score['count']
                    entry[f"emotion_hartmann_{emotion_score['label']}_ratio"] = emotion_score['ratio']

                entry[f"emotion_hartmann_label"] = doc._.emotion_label
                out_arr.append(entry)
            emotion_node:Document = self.create_node(doc._.emotion_label)
            text_node:Document = self.get_document(self.annotated_node, {"_key": text_key})
            _ = self.create_edge(text_node, emotion_node, entry)
            
        out_df: pd.DataFrame = pd.DataFrame(out_arr)
        out_df.fillna(0, inplace=True)

        return out_df









