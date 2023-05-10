from pyArango.document import Document
from cag.framework.annotator.element.orchestrator import PipeOrchestrator
import pandas as pd

from cag.framework.annotator.pipe.linguistic.hedge import HedgeFactory


class HedgePipeOrchestrator(PipeOrchestrator):
    def create_node(self, hedge_label: str) -> Document:
        data = {"label": hedge_label}
        return self.upsert_node(self.node_name, data, alt_key=["label"])

    def create_edge(
        self, _from: Document, _to: Document, hedge_attrs
    ) -> Document:
        return self.upsert_edge(self.edge_name, _from, _to, hedge_attrs)

    def save_annotations(self, annotated_texts: list) -> pd.DataFrame:
        out_arr = []
        for doc, context in annotated_texts:
            text_key = context["_key"]

            res_df = pd.DataFrame(doc._.hedge)
            dominant = res_df.iloc[res_df["size"].argmax()]["label"]
            if doc._.hedge is not None and len(doc._.hedge) > 0:
                for hedge_dict in doc._.hedge:
                    if hedge_dict["size"] > 0:
                        entry = {}
                        label = hedge_dict["size"]
                        entry["count"] = hedge_dict["size"]
                        entry["ratio"] = hedge_dict["ratio"]
                        entry["token_lst"] = list(set(hedge_dict["words"]))
                        entry["is_dominant"] = (
                            True if label == dominant else False
                        )
                        entry["metadata"] = HedgeFactory._METADATA_
                        hedge_node: Document = self.create_node(label)
                        text_node: Document = self.get_document(
                            self.annotated_node, {"_key": text_key}
                        )
                        _ = self.create_edge(text_node, hedge_node, entry)
                        record = {f"hedge_{x}": y for x, y in entry.items()}
                        record["hedge_label"] = label
                        record["text_key"] = text_key

                        out_arr.append(record)
        out_df: pd.DataFrame = pd.DataFrame(out_arr)

        return out_df
