
from pyArango.document import Document
from cag.framework.annotator.element.orchestrator import PipeOrchestrator
import pandas as pd


class KeyphrasePipeOrchestrator(PipeOrchestrator):

    def create_node(self, name) -> Document:
        node = self.upsert_node(self.node_name, {"name": name}, alt_key=["name"])
        return node

    def create_edge(
        self, _from: Document, _to: Document, positions
    ) -> Document:
        self.upsert_edge(self.edge_name, _from, _to, {"token_position_lst": positions,
                                                      "count":len(positions)})
    
    def save_annotations(self, annotated_text: "[]"):
        for doc, context in annotated_text:
            text_key = context["_key"]
            for keyphrase, positions in zip(doc._.keyphrases, 
                                            doc._.keyphrases_char_positions):
                # 1. insert the keyphrase node
                keyphrase_node = self.create_node(keyphrase)
                text_node: Document = self.get_document(
                    self.annotated_node, {"_key": text_key}
                )
                #2. insert the edge
                self.create_edge(text_node, keyphrase_node, positions)