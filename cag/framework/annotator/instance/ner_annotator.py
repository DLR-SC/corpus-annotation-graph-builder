import pandas as pd

from nlpaf.annotator.orchestrator import PipeOrchestrator


class NamedEntityPipeOrchestrator(PipeOrchestrator):
    def save_annotations(self, annotated_texts: "[]"):
        for doc, context in annotated_texts:
            row = {self.input_id: context[self.input_id]}
            for ent in doc.ents:
                ner_txt = ent.text
                ner_type = ent.label_

                # entity.start_char, entity.end_char
