from pyArango.document import Document
from cag.framework.annotator.element.orchestrator import PipeOrchestrator
import pandas as pd


class EmpathPipeOrchestrator(PipeOrchestrator):
    def create_node(self, empath_cat) -> Document:
        data = {"category": empath_cat}
        return self.upsert_node(self.node_name, data, alt_key="category")

    def create_edge(self, from_: Document, to_: Document, entry) -> Document:
        return self.upsert_edge(self.edge_name, from_, to_, edge_attrs=entry)

    col = "empath"
    col_position = "empath_position"
    col_words = "empath_words"

    def save_annotations(self, annotated_texts: "[]"):
        out_arr = []
        for doc, context in annotated_texts:
            text_key = context["_key"]

            for category, count in doc._.empath_count.items():
                if count > 0:
                    empath_node: Document = self.create_node(category)
                    text_node: Document = self.get_document(
                        self.annotated_node, {"_key": text_key}
                    )

                    entry = {
                        "count": doc._.empath_count[category],
                        "ratio": doc._.empath_ratio[category],
                        "token_position_lst": doc._.empath_positions[category],
                        "token_lst": doc._.empath_words[category],
                    }

                    _: Document = self.create_edge(
                        text_node, empath_node, entry
                    )

                    record = {f"empath_{x}": y for x, y in entry.items()}
                    record["empath_category"] = category
                    record["text_key"] = text_key
                    out_arr.append(record)
        out_df: pd.DataFrame = pd.DataFrame(out_arr)

        return out_df
