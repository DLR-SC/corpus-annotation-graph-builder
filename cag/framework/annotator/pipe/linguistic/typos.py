from spacy.language import Language
from spacy.tokens import Span, Doc
from transformers import AutoConfig, AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from transformers.utils import logging


# REQUIRES sentencizer
# https://huggingface.co/m3hrdadfi/typo-detector-distilbert-en?text=The+review+thoroughla+assessed+all+aspects+of+JLENS+SuR+and+CPG+esign+maturit+and+confidence+.
@Language.factory("typo_component")
class TypoFactory:
    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar()

        model_name_or_path = "m3hrdadfi/typo-detector-distilbert-en"
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForTokenClassification.from_pretrained(
            model_name_or_path, config=AutoConfig.from_pretrained(model_name_or_path)
        )
        self.transformer_nlp = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=tokenizer,
            aggregation_strategy="average",
        )

        if not Span.has_extension("typos"):
            Span.set_extension("typos", default=None)

        if not Doc.has_extension("doc_typos"):
            Doc.set_extension("doc_typos", default=None)

    def __call__(self, doc):
        all_typos = []
        for sentence in doc.sents:
            txt = sentence.text
            typos = [txt[r["start"] : r["end"]] for r in self.transformer_nlp(txt)]
            all_typos.extend(typos)
            sentence._.set("typos", {"count": len(typos), "words": typos})
        doc._.set(
            "doc_typos",
            {
                "counter": [{x: all_typos.count(x)} for x in set(all_typos)],
                "count": len(all_typos),
            },
        )
        return doc
