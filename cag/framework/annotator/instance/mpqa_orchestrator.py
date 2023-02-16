import pandas as pd
from pyArango.document import Document
from ..element.orchestrator import PipeOrchestrator
from ..pipe.linguistic.mpqa import MpqaArgFactory


class MpqaPipeOrchestrator(PipeOrchestrator):
    def create_node(self, mpqa_label: str) -> Document:
        data = {"label": mpqa_label}
        return self.upsert_node(self.node_name, data, alt_key=["label"])

    def create_edge(
        self, _from: Document, _to: Document, mpqa_attrs
    ) -> Document:
        return self.upsert_edge(self.edge_name, _from, _to, mpqa_attrs)

    def save_annotations(self, annotated_texts: list) -> pd.DataFrame:
        out_arr = []

        for doc, context in annotated_texts:
            text_key = context["_key"]

            text_node: Document = self.get_document(
                self.annotated_node, {"_key": text_key}
            )

            mpqa_exts = [
                x for x in doc._.doc_extensions if x.startswith("mpqa_")
            ]

            # logger.debug(mpqa_exts

            for label in mpqa_exts:
                if doc._.get(label) > 0:
                    mpqa_node: Document = self.create_node(label)
                    entry = {
                        "count": doc._.get(label),
                        "ratio": round((doc._.get(label) / doc.__len__()), 3),
                        "metadata": MpqaArgFactory.__METADATA__,
                    }
                    _ = self.create_edge(text_node, mpqa_node, entry)
                    # for the dataframe
                    record = {f"mpqa_{x}": y for x, y in entry.items()}
                    record["label"] = label
                    record["text_key"] = text_key

                    out_arr.append(record)

            all_args_spans_count = doc._.mpqa_args_count
            if all_args_spans_count > 0:
                label = "MPQA_Arguments"
                mpqa_node: Document = self.create_node(label)
                entry = {
                    "count": doc._.mpqa_args_count,
                    "ratio": doc._.mpqa_token_ratio,
                    "metadata": MpqaArgFactory.__METADATA__,
                }

                _ = self.create_edge(text_node, mpqa_node, entry)

                # for the dataframe
                record = {f"mpqa_{x}": y for x, y in entry.items()}
                record["label"] = label
                record["text_key"] = text_key

                out_arr.append(record)

        out_df: pd.DataFrame = pd.DataFrame(out_arr)

        return out_df
