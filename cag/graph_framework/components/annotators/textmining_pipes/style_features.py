
#### HELPERS ####
import spacy
from spacy_arguing_lexicon import ArguingLexiconParser
from empath import Empath
from spacy.language import Language
from spacy.tokens import Token, Span, Doc


def set_extension_(ext, default = None):
    if not Doc.has_extension(ext):
        Doc.set_extension(ext, default=default)


### END OF Helpers ####


### Pipes ###
@Language.component("empath_component")
def empath_component_function(doc:Doc):
    lexicon = Empath()
    empath_dic = lexicon.analyze(doc.text, normalize=False)
    for k,v in empath_dic.items():
        col = "{}_{}".format("empath", k)
        set_extension_(col, default=None)
        doc._.set(col, v)
    return doc

@Language.component("mpqa_counter")
def mpqa_counter_function(doc):
    arguments = list(doc._.arguments.get_argument_spans_and_matches())

    total_arg_words = 0

    for arg in arguments:
        arg_span = arg[0]
        label = arg_span.label_

        col = "{}_{}".format("mpqa", label)
        set_extension_(col, default = 0)

        doc._.set(col, doc._.get(col)+1)

        total_arg_words += arg_span.__len__()

    set_extension_("mpqa_token_ratio", default = 0.0)
    set_extension_("count_mpqa_args", default = 0)

    doc._.mpqa_token_ratio =round(float(total_arg_words) / float(doc.__len__()), 3)
    doc._.count_mpqa_args = len(arguments)

    return doc


@Language.factory("mpqa_parser")
def mpqa_parser(nlp, name):
    return ArguingLexiconParser(lang=nlp.lang)