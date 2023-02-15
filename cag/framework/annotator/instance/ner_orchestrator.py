from pyArango.document import Document
import pyArango
from cag.framework.annotator.element.orchestrator import PipeOrchestrator


class NamedEntityPipeOrchestrator(PipeOrchestrator):
    def create_node(self, ner_txt, ner_type) -> pyArango.document.Document:
        data = {"name": ner_txt, "type": ner_type}
        return self.upsert_node(self.node_name, data, alt_key=["name", "type"])

    def create_edge(self, _from: Document, _to: Document, entity) -> Document:
        position = (entity.start_char, entity.end_char)
        edge_dict: dict = self.get_edge_attributes(self.edge_name, _from, _to)
        edge = self.get_document(self.edge_name, edge_dict)

        lst_positions = [position]
        count: int = 1
        if edge is not None:
            if position not in edge.token_position_lst:
                if edge.token_position_lst is not None:
                    lst_positions.extend(edge.token_position_lst)
                if edge.count is not None:
                    count = count + edge.count

            else:
                return edge
        return self.upsert_edge(
            self.edge_name,
            _from,
            _to,
            edge_attrs={"count": count, "token_position_lst": lst_positions},
        )

    def save_annotations(self, annotated_texts: "[]"):
        for doc, context in annotated_texts:
            text_key = context["_key"]
            for ent in doc.ents:
                ner_txt = ent.text
                ner_type = ent.label_
                ner_node: Document = self.create_node(ner_txt, ner_type)
                text_node: Document = self.get_document(
                    self.annotated_node, {"_key": text_key}
                )
                _: Document = self.create_edge(text_node, ner_node, ent)
        return None
