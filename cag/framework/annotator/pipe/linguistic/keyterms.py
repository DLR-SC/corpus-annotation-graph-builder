from typing import ClassVar
from spacy_arguing_lexicon import ArguingLexiconParser

from spacy.language import Language
from spacy.tokens import Doc

from transformers.utils import logging

import requests
import json
from dotenv import load_dotenv

import os


def get_keyterms(text_string, max_num=10):
    load_dotenv()
    data = json.dumps({
        "payload": {
            "text": text_string
        },
        "settings": {
            "ne_parts": 4,
            "wiki_parts": 7,
            "clean_pos": [
                "NOUN",
                "ADJ",
                "PROPN"
            ],
            "clean_len": 3,
            "clean_stopwords": ["datum"],
            "rank_window": 5,
            "rank_alpha": 0.85,
            "rank_beta": -0.9,
            "rank_groups": 20,
            "rank_stars": 3,
            "condense_percentage": 25
        }
    })
    res = requests.post(
        os.getenv('CORPUS_API_URL') + "keyterms?topn=" + str(max_num),
        headers={
            'accept': 'application/json',
            'ACCESS_TOKEN': os.getenv('CORPUS_PUB_API_KEY'),
            'Content-Type': 'application/json'
        },
        data=data,
        verify=False
    )
    return res.json()


@Language.factory("keyterms_component")
class KeyTerms:
    __METADATA__: ClassVar = "KeyTermsComponent from Metodio"

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar()
        if not Doc.has_extension("keyterms"):
            Doc.set_extension("keyterms", default=[])

    def __call__(self, doc):

        text: str = doc.text
        keyterms = get_keyterms(text)
        doc._.set("keyterms", keyterms)

        return doc
