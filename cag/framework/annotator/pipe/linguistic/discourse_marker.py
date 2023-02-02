from simpletransformers.ner import NERModel
from spacy.language import Language
from spacy.tokens import Token, Span, Doc


@Language.factory("discoursemarker_component")
class DiscourseMarkerFactory:
    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp

        # Discourse marker prediction / discourse connective prediction pretrained model
        # https://huggingface.co/sileod/roberta-base-discourse-marker-prediction?text=But+no%2C+Amazon+selling+3D+printers+is+not+new.<%2Fs><%2Fs>The+promise+of+3D+printing+is+very+great.
        tokenizer = AutoTokenizer.from_pretrained(
            "sileod/roberta-base-discourse-marker-prediction"
        )

        model = AutoModelForSequenceClassification.from_pretrained(
            "sileod/roberta-base-discourse-marker-prediction"
        )

        self.transformer_nlp = pipeline(
            "text-classification", model=model, tokenizer=tokenizer
        )
        if not Doc.has_extension("discourse_marker"):
            Doc.set_extension("discourse_marker", default=None)

    def __call__(self, doc):
        all_typos = []
        for sentence in doc.sents:
            pass
        # where text is sentence 1 and sentence 2
        self.transformer_nlp(doc.text)
        return doc
