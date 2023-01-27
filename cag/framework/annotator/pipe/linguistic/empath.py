
#### HELPERS ####
from collections import defaultdict

import spacy
from spacy_arguing_lexicon import ArguingLexiconParser
from empath import Empath
from empath import helpers
from spacy.language import Language
from spacy.tokens import Token, Span, Doc

from transformers.utils import logging


class EmpathExtended(Empath):
    def __init__(self):
        super().__init__()

    def analyze(self,doc,categories=None,tokenizer="default",normalize=False):
        if isinstance(doc,list):
            doc = "\n".join(doc)
        if tokenizer == "default":
            tokenizer = helpers.default_tokenizer
        elif tokenizer == "bigrams":
            tokenizer = helpers.bigram_tokenizer
        if not hasattr(tokenizer,"__call__"):
            raise Exception("invalid tokenizer")
        if not categories:
            categories = self.cats.keys()
        invcats = defaultdict(list)
        for k in categories:
           for t in self.cats[k]: invcats[t].append(k)
        count = {}
        ratio = {}
        tokens = 0.0
        for cat in categories: count[cat] = 0.0
        words_position = {}
        words = {}
        for tk in tokenizer(doc):
            tokens += 1.0
            for cat in invcats[tk]:
                count[cat]+=1.0
                if cat not in words_position.keys():
                    words_position[cat] = [(i, (i+len(tk))) for i in range(len(doc)) if doc.startswith(tk, i)]
                    words[cat] = []
                words[cat].append(tk)

        #if normalize:
        for cat in count.keys():
            if tokens == 0:
                return None
            else:
                ratio[cat] = count[cat] / tokens
        return count, ratio, words_position, words


@Language.factory("empath_component")
class EmpathFactory:
    EMPATH_CUSTOM_LABEL_LST = ["empath_count", "empath_ratio", "empath_positions", "empath_words"]

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar()
        self.lexicon = EmpathExtended()

        for cat in self.lexicon.cats:
            ext: str  = f"empath_{cat}"
            if not Doc.has_extension(ext):
                Doc.set_extension(ext, default=None)

        for ext in EmpathFactory.EMPATH_CUSTOM_LABEL_LST:
            if not Doc.has_extension(ext):
                Doc.set_extension(ext, default=None)

    def __call__(self, doc):
        empath_dic, ratios, positions, words = self.lexicon.analyze(doc.text)

        empath_caregories = [k for k,v in empath_dic.items() if v > 0.0]
        doc._.set("empath_count",    {k:v for k,v in empath_dic.items() if k in empath_caregories})
        doc._.set("empath_ratio",    {k:v for k,v in ratios.items() if k in empath_caregories})
        doc._.set("empath_positions", {k:v for k,v in positions.items() if k in empath_caregories})
        doc._.set("empath_words",    {k:v for k,v in words.items() if k in empath_caregories})


        return doc
