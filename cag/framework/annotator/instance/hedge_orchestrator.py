from pyArango.document import Document
from cag.framework.annotator.element.orchestrator import PipeOrchestrator
import pandas as pd


class HedgeOrchestrator(PipeOrchestrator):
    def create_node(self, emotion_label: str) -> Document:
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
            row = {self.input_id: context[self.input_id]}

            if doc._.hedge is not None and len(doc._.hedge) > 0:
                for hedge_dict in doc._.hedge:
                    row[f"hedge_{hedge_dict['label']}_count"] = hedge_dict[
                        "size"
                    ]
                    row[f"hedge_{hedge_dict['label']}_ratio"] = hedge_dict[
                        "ratio"
                    ]
                    row[f"hedge_{hedge_dict['label']}_words"] = hedge_dict[
                        "words"
                    ]

                res_df = pd.DataFrame(doc._.hedge)

                row["hedge_dominant"] = res_df.iloc[res_df["size"].argmax()][
                    "label"
                ]
                out_arr.append(row)
        out_df: pd.DataFrame = pd.DataFrame(out_arr)

        return out_df
