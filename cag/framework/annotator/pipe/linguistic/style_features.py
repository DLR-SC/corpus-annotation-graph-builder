#### HELPERS ####
from collections import defaultdict

import spacy
from spacy_arguing_lexicon import ArguingLexiconParser
from empath import Empath
from empath import helpers
from spacy.language import Language
from spacy.tokens import Token, Span, Doc


def set_extension_(ext, default=None):
    if not Doc.has_extension(ext):
        Doc.set_extension(ext, default=default)


### END OF Helpers ####


### Pipes ###


class EmpathExtended(Empath):
    def __init__(self):
        super().__init__()

    def analyze(
        self, doc, categories=None, tokenizer="default", normalize=False
    ):
        if isinstance(doc, list):
            doc = "\n".join(doc)
        if tokenizer == "default":
            tokenizer = helpers.default_tokenizer
        elif tokenizer == "bigrams":
            tokenizer = helpers.bigram_tokenizer
        if not hasattr(tokenizer, "__call__"):
            raise Exception("invalid tokenizer")
        if not categories:
            categories = self.cats.keys()
        invcats = defaultdict(list)
        for k in categories:
            for t in self.cats[k]:
                invcats[t].append(k)
        count = {}
        ratio = {}
        tokens = 0.0
        for cat in categories:
            count[cat] = 0.0
        words_position = {}
        words = {}
        for tk in tokenizer(doc):
            tokens += 1.0
            for cat in invcats[tk]:
                count[cat] += 1.0
                if cat not in words_position.keys():
                    words_position[cat] = [
                        (i, (i + len(tk)))
                        for i in range(len(doc))
                        if doc.startswith(tk, i)
                    ]
                    words[cat] = []
                words[cat].append(tk)

        # if normalize:
        for cat in count.keys():
            if tokens == 0:
                return None
            else:
                ratio[cat] = count[cat] / tokens
        return count, ratio, words_position, words


@Language.component("empath_component")
def empath_component_function(doc: Doc):
    lexicon = EmpathExtended()
    empath_dic, ratios, positions, words = lexicon.analyze(doc.text)

    col_count = "empath_count"
    col_ratio = "empath_ratio"
    col_position = "empath_positions"
    col_words = "empath_words"

    set_extension_(col_count, default=None)
    set_extension_(col_ratio, default=None)
    set_extension_(col_position, default=None)
    set_extension_(col_words, default=None)

    empath_caregories = [k for k, v in empath_dic.items() if v > 0.0]
    doc._.set(
        col_count,
        {k: v for k, v in empath_dic.items() if k in empath_caregories},
    )
    doc._.set(
        col_ratio, {k: v for k, v in ratios.items() if k in empath_caregories}
    )
    doc._.set(
        col_position,
        {k: v for k, v in positions.items() if k in empath_caregories},
    )
    doc._.set(
        col_words, {k: v for k, v in words.items() if k in empath_caregories}
    )

    return doc


@Language.component("mpqa_counter")
def mpqa_counter_function(doc):
    arguments = list(doc._.arguments.get_argument_spans_and_matches())

    total_arg_words = 0

    for arg in arguments:
        arg_span = arg[0]
        label = arg_span.label_

        col = "{}_{}".format("mpqa", label)
        set_extension_(col, default=0)

        doc._.set(col, doc._.get(col) + 1)

        total_arg_words += arg_span.__len__()

    set_extension_("mpqa_token_ratio", default=0.0)
    set_extension_("count_mpqa_args", default=0)

    doc._.mpqa_token_ratio = round(
        float(total_arg_words) / float(doc.__len__()), 3
    )
    doc._.count_mpqa_args = len(arguments)

    return doc


@Language.factory("mpqa_parser")
def mpqa_parser(nlp, name):
    return ArguingLexiconParser(lang=nlp.lang)
