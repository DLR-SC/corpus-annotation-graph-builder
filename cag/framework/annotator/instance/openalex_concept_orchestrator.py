from pyArango.document import Document
from cag.framework.annotator.element.orchestrator import PipeOrchestrator
import pandas as pd

from cag.framework.annotator.pipe.linguistic.oaconcept import OpenAlexConcept


class OAConceptPipeOrchestrator(PipeOrchestrator):
    def create_node(self, oa_id, name) -> Document:
        data = {"oa_id": oa_id,
                "name": name}
        return self.upsert_node(self.node_name,
                                data,
                                alt_key=["oa_id", "name"])

    def create_edge(self, from_: Document, to_: Document, entry) -> Document:
        return self.upsert_edge(self.edge_name, from_, to_, edge_attrs=entry)

    def save_annotations(self, annotated_texts: "[]"):
        out_arr = []
        for doc, context in annotated_texts:
            text_key = context["_key"]

            for level, oa_concepts in doc._.oa_concepts.items():
                for oa_concept_name, oa_concept_id in oa_concepts:
                    oaconcept_node: Document = self.create_node(oa_concept_id,
                                                                oa_concept_name)
                    text_node: Document = self.get_document(
                        self.annotated_node, {"_key": text_key}
                    )

                    entry = {
                        "level": level,
                        "metadata": OpenAlexConcept.__METADATA__
                    }

                    _: Document = self.create_edge(
                        text_node, oaconcept_node, entry
                    )

                    record = {f"oaconcept_{x}": y for x, y in entry.items()}
                    record["oaconcept_id"] = oa_concept_id
                    record["oaconcept_name"] = oa_concept_name
                    record["text_key"] = text_key
                    out_arr.append(record)
        out_df: pd.DataFrame = pd.DataFrame(out_arr)

        return out_df
