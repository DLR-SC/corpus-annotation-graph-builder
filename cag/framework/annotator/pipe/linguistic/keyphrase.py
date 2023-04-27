from spacy.matcher import PhraseMatcher

from spacy.util import filter_spans
from spacy.language import Language
from spacy.tokens import Doc


@Language.factory("keyphrase_component")
class KeyphraseFactory:
    _KEYPHRASE_ = "keyphrases"
    _KEYPHRASE_POSITION_ = "keyphrases_char_positions"

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        self.matcher = PhraseMatcher(nlp.vocab)

        if not Doc.has_extension(KeyphraseFactory._KEYPHRASE_):
            Doc.set_extension(KeyphraseFactory._KEYPHRASE_)
        if not Doc.has_extension(KeyphraseFactory._KEYPHRASE_POSITION_):
            Doc.set_extension(KeyphraseFactory._KEYPHRASE_POSITION_)

    def __call__(self, doc):
        keywords = doc._.keywords
        patterns = [self.nlp.make_doc(text) for text in keywords]

        self.matcher.add('keyphrases', patterns)
        matches = self.matcher(doc)

        doc_kws = []
        tokens_positions = []
        spans = [doc[start:end] for _, start, end in matches]
        for span in filter_spans(spans):
            if span.text in keywords:
                tokens_positions.append(tuple(span.start_char, span.end_char))
                doc_kws.append(span.text)
        doc._.keyphrases = doc_kws
        doc._.keyphrases_char_positions = tokens_positions
        return doc

