import pandas as pd
from pyArango.document import Document
from ..element.orchestrator import PipeOrchestrator
from ..pipe.linguistic.toxicity import ToxicityFactory


class ToxicityOrchestrator(PipeOrchestrator):
    def create_node(self, label: str) -> Document:
        data = {"label": label}
        return self.upsert_node(self.node_name, data, alt_key=["label"])

    def create_edge(self, _from: Document, _to: Document, attrs) -> Document:
        return self.upsert_edge(self.edge_name, _from, _to, attrs)

    def save_annotations(self, annotated_texts: list) -> pd.DataFrame:
        out_arr = []
        for doc, context in annotated_texts:
            text_key = context["_key"]
            text_node: Document = self.get_document(
                self.annotated_node, {"_key": text_key}
            )
            res_df = pd.DataFrame(doc._.toxicity)
            dominant = res_df.iloc[res_df["count"].argmax()]["label"]
            if doc._.toxicity is not None:
                for toxicity_dict in doc._.toxicity:
                    if toxicity_dict["count"] > 0:
                        toxicity_label = toxicity_dict["label"]
                        toxicity_node: Document = self.create_node(
                            toxicity_label
                        )

                        entry = {}
                        entry["count"] = toxicity_dict["count"]
                        entry["ratio"] = toxicity_dict["ratio"]
                        entry["score_mean"] = toxicity_dict["score_mean"]
                        entry["is_dominant"] = (
                            True if toxicity_label == dominant else False
                        )
                        entry["metadata"] = ToxicityFactory._METADATA_
                        entry[
                            "sentence_index_w_highest_score"
                        ] = toxicity_dict["sentence_index_w_highest_score"]

                        entry["highest_score"] = toxicity_dict["highest_score"]
                        _ = self.create_edge(text_node, toxicity_node, entry)

                        record = {f"toxicity_{x}": y for x, y in entry.items()}
                        record["label"] = toxicity_label
                        record["text_key"] = text_key
                        out_arr.append(record)
        out_df: pd.DataFrame = pd.DataFrame(out_arr)

        return out_df
