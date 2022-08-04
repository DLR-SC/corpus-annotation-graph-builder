
from pyArango.document import Document
import pyArango
from cag.graph_framework.components.annotators.element.annotator import Annotator


class EmpathAnnotator(Annotator):

    def create_vertex(self, empath_cat) -> Document:
        data = {"category": empath_cat}
        return self.upsert_vert(self.vertex_name, data, alt_key="category")

    def create_edge(self, from_:Document, to_:Document,
                    count: int,
                    ratio: float,
                    token_position_lst,
                    token_lst) -> Document:
        return self.upsert_link(self.edge_name,
                                from_,
                                to_,
                                edge_attrs={
                                        "count": count,
                                        "ratio": ratio,
                                        "token_position_lst":token_position_lst, # array of tuples [(start, end), (start, end)]
                                        "token_lst": token_lst,  # array of tuples [(start, end), (start, end)]
                                    }
                                )

    col = "empath"
    col_position = "empath_position"
    col_words = "empath_words"
    def save_annotations(self, annotated_texts: "[]"):
        for doc, context in annotated_texts:
            text_key = context["_key"]

            for category, count in doc._.empath_count.items():
                empath_vertex: Document = self.create_vertex(category)
                text_vertex: Document = self.get_document(self.annotated_vertex, {"_key": text_key})
                empath_edge: Document = self.create_edge(text_vertex, empath_vertex,
                                                      doc._.empath_count[category],
                                                      doc._.empath_ratio[category],
                                                      doc._.empath_positions[category],
                                                      doc._.empath_words[category])









