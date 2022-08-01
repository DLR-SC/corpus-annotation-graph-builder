from typing import ClassVar, List

from pyArango.document import Document

from cag.utils.config import Config
from .annotator import Annotator


class NamedEntityAnnotator(Annotator):

    def __init__(self, annotators_config, conf: Config = None):
        super().__init__(annotators_config, conf)

    def create_vertex(self, ner_txt, ner_type):
        data = {"name": ner_txt, "type": ner_type}
        return self.upsert_vert(self.vertex_name, data, alt_key=["name", "type"])

    def create_edge(self, entity, from_, to_):
        position = (entity.start_char, entity.end_char)
        edge_dict: dict = self._get_edge_dict(self.edge_name, from_, to_)
        edge = self.get_document(self.edge_name, edge_dict)

        lst_positions = [position]
        count: int = 1
        if edge is not None:
            if position not in edge.annotation_position:
                lst_positions.extend(edge.annotation_position)
                count = count + edge.count
            else:
                return edge
        return self.upsert_link(self.edge_name,
                                from_,
                                to_,
                                edge_attrs={"counter": count,
                                            "positions": lst_positions
                                            }
                             )

    def save_annotations(self, annotated_texts:"[]"):
        for doc, context in annotated_texts:
            text_key = context["_key"]
            for ent in doc.ents:
                ner_txt = ent.text
                ner_type = ent.label_
                ner_vertex:Document = self.create_vertex(ner_txt, ner_type)
                text_vertex:Document = self.get_document(self.annotated_vertex, {"_key": text_key})
                ner_edge :Document = self.create_edge(ent, text_vertex, ner_vertex)







