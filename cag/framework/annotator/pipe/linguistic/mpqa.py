
from spacy_arguing_lexicon import ArguingLexiconParser

from spacy.language import Language
from spacy.tokens import Token, Span, Doc

from transformers.utils import logging


@Language.factory("mpqa_arg_component")
class MpqaArgFactory:
    MPQA_ARG_LABEL_LST = [    
            'assessments',
            'doubt',
            'authority',
            'emphasis',
            'necessity',
            'causation',
            'generalization',
            'structure',
            'conditionals',
            'inconsistency',
            'possibility',
            'wants',
            'contrast',
            'priority',
            'difficulty',
            'inyourshoes',
            'rhetoricalquestion',
           
        ]

    MPQA_ARG_CUSTOM_LABEL_LST = [
        'argumentative', 
        'token_ratio',
        'args_count'
    ]

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar()
        all_labels = [f"mpqa_{x}" for x in  MpqaArgFactory.MPQA_ARG_LABEL_LST+ MpqaArgFactory.MPQA_ARG_CUSTOM_LABEL_LST]
        for label in all_labels:
            if not Doc.has_extension(label):
                Doc.set_extension(label, default=0)

    def __call__(self, doc):
        arguments = list(doc._.arguments.get_argument_spans_and_matches())
        doc._.mpqa_argumentative = len(arguments)
        total_arg_words = 0

        for arg in arguments:
            arg_span = arg[0]
            label = arg_span.label_

            col = "{}_{}".format("mpqa", label)
            doc._.set(col, doc._.get(col)+1)

            total_arg_words += arg_span.__len__()

        doc._.mpqa_token_ratio =round(float(total_arg_words) / float(doc.__len__()), 3)
        doc._.mpqa_args_count = len(arguments)

        return doc


@Language.factory("mpqa_parser")
def mpqa_parser(nlp, name):
    return ArguingLexiconParser(lang=nlp.lang)