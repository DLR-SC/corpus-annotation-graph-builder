from typing import ClassVar
from spacy_arguing_lexicon import ArguingLexiconParser

from spacy.language import Language
from spacy.tokens import Doc

from transformers.utils import logging

import requests
import json
from dotenv import load_dotenv

import os


def get_media_topics(text_string, text_lng="en"):
    load_dotenv()
    taxo_parms_dict = {
        "en": {
            "taxonomy": "IptcMedia",
            "language": "en",
            "tuning_parameters": {
                "use_descriptions": True,
                "language_model": "all-MiniLM-L6-v2",
                "top_k": 10,
                "min_similarity": 0.25,
                "title_weight": 1.5,
                "saturation": 1.5,
                "min_agg": 0.25,
                "top_percent": 80,
                "second_percent": 80,
                "min_hscore": 0.25,
                "max_baseconcepts": 7,
                "max_paths": 2
            },
        },
        "de": {
            "taxonomy": "IptcMedia",
            "language": "de",
            "tuning_parameters": {
                "use_descriptions": True,
                "language_model": "paraphrase-multilingual-MiniLM-L12-v2",
                "top_k": 10,
                "min_similarity": 0.25,
                "title_weight": 1.5,
                "saturation": 1.5,
                "min_agg": 0.25,
                "top_percent": 80,
                "second_percent": 80,
                "min_hscore": 0.25,
                "max_baseconcepts": 7,
                "max_paths": 2
            },
        },
    }
    if not taxo_parms_dict.get(text_lng):
        return None
    data = json.dumps({
        "payload": {
            "text": text_string
        },
        "taxo_parms": taxo_parms_dict[text_lng]
    })
    res = requests.post(
        os.getenv('CORPUS_API_URL') + "taxonomytags",
        headers={
            'accept': 'application/json',
            'ACCESS_TOKEN': os.getenv("CORPUS_PUB_API_KEY"),
            'Content-Type': 'application/json'
        },
        data=data,
        verify=False
    )
    return res.json()


@Language.factory("iptc_media_topic_component")
class IPTCMediaTopic:
    __METADATA__: ClassVar = "IPTCMediaTopic"

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar()
        if not Doc.has_extension("media_topic"):
            Doc.set_extension("media_topic", default=[])

    def __call__(self, doc):

        text: str = doc.text
        doc._.set("media_topic", get_media_topics(text))

        return doc


@Language.factory("iptc_media_topic_de_component")
class IPTCMediaDETopic:
    __METADATA__: ClassVar = "IPTCMediaDETopic"

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar()
        if not Doc.has_extension("media_topic"):
            Doc.set_extension("media_topic", default=[])

    def __call__(self, doc):

        text: str = doc.text
        doc._.set("media_topic", get_media_topics(text,  text_lng="de"))

        return doc
