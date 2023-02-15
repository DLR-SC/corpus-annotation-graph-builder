import pandas as pd

from nlpaf.annotator.orchestrator import PipeOrchestrator
from nlpaf import logger
from spacy.tokens import Doc


class MpqaPipeOrchestrator(PipeOrchestrator):
    def create_node(self, emotion_label: str) -> pyArango.document.Document:
        data = {"label": emotion_label}
        return self.upsert_node(self.node_name, data, alt_key=["label"])

    def create_edge(
        self, _from: Document, _to: Document, emotion_attrs
    ) -> Document:
        # edge_dict: dict = self.get_edge_attributes(self.edge_name, _from, _to)
        # edge = self.get_document(self.edge_name, edge_dict)

        return self.upsert_edge(self.edge_name, _from, _to, emotion_attrs)

    def save_annotations(self, annotated_texts: list) -> pd.DataFrame:
        out_arr = []

        for doc, context in annotated_texts:
            d: Doc = doc
            mpqa_exts = [
                x for x in d._.doc_extensions if x.startswith("mpqa_")
            ]
            # logger.debug(mpqa_exts
            row = {self.input_id: context[self.input_id]}

            for mpqa_ext in mpqa_exts:
                row[f"{mpqa_ext}"] = doc._.get(mpqa_ext)

            row["mpqa_token_ratio"] = doc._.mpqa_token_ratio
            row["mpqa_args_count"] = doc._.mpqa_args_count
            out_arr.append(row)
        out_df: pd.DataFrame = pd.DataFrame(out_arr)

        return out_df
