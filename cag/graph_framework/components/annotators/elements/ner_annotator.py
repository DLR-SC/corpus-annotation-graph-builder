from .annotator import Annotator

class NamedEntityAnnotator(Annotator):

    def __init__(self, db):
        super().__init__(name = "named_entity",
              vertex_class_path = "cag.annotators.components.nodes.NamedEntityNode",
              edge_class_path = "cag.annotators.components.nodes.HasAnnotation",
              database = db,
              annotation_level = Annotator.LEVEL_TEXT)
        self.name = self.vertex_class_path.split(".")[-1]



    def create_vertex(self, ner_txt, ner_type):
        pass
    def save_annotations(self, annotated_texts:"[]"):

        for doc in annotated_texts:
            entity_lst = []
            for ent in doc.ents:
                entity_name = ent.text
                label = ent.label_
                # check if entity label already exists
                ner_vertex_exist = False
                if not ner_vertex_exist:
                    # create entity
                    # create edge with count 1
                    pass
                else: # if it exists
                    # check if edge exists
                    ner_edge_exist = False
                    if ner_edge_exist:
                        pass
                        #update edge and increment by one
                    else:
                        # create edhe and set counter to 1
                        pass





