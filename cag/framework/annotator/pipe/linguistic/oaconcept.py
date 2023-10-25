from typing import ClassVar
from spacy_arguing_lexicon import ArguingLexiconParser

from spacy.language import Language
from spacy.tokens import Doc

from transformers.utils import logging

import requests
import json
from dotenv import load_dotenv, find_dotenv

import os


def get_oaconcepts(text_string, text_lng="en"):
    load_success = load_dotenv()
    if not load_success:
        # try loading '.env' file from current working dir
        load_dotenv(find_dotenv(usecwd=True))

    taxo_parms_dict = {
        "enScience": {
            "taxonomy": "OpenAlex",
            "language": "en",
            "tuning_parameters": {
                "use_descriptions": True,
                "language_model": "all-MiniLM-L6-v2",
                "top_k": 10,
                "min_similarity": 0.35,
                "title_weight": 1.5,
                "saturation": 1.5,
                "min_agg": 0.35,
                "top_percent": 80,
                "second_percent": 80,
                "min_hscore": 0.35,
                "max_baseconcepts": 7,
                "max_paths": 2
            },
        },
        "deScience": {
            "taxonomy": "OpenAlex",
            "language": "de",
            "tuning_parameters": {
                "use_descriptions": True,
                "language_model": "paraphrase-multilingual-MiniLM-L12-v2",
                "top_k": 10,
                "min_similarity": 0.4,
                "title_weight": 1.5,
                "saturation": 1.5,
                "min_agg": 0.4,
                "top_percent": 80,
                "second_percent": 80,
                "min_hscore": 0.4,
                "max_baseconcepts": 7,
                "max_paths": 2
            },
        },
    }
    if not taxo_parms_dict.get(text_lng + "Science"):
        return None
    data = json.dumps({
        "payload": {
            "text": text_string
        },
        "taxo_parms": taxo_parms_dict[text_lng + "Science"]
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



@Language.factory("openalex_concept_component")
class OpenAlexConcept:
    __METADATA__: ClassVar = "OpenAlexConcept from Metodio"

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar()
        if not Doc.has_extension("oa_concepts"):
            Doc.set_extension("oa_concepts", default=[])

    def __call__(self, doc):

        text: str = doc.text
        doc._.set("oa_concepts", get_oaconcepts(text))

        return doc
    
@Language.factory("openalex_concept_de_component")
class OpenAlexDEConcept:
    __METADATA__: ClassVar = "OpenAlexDEConcept"

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar()
        if not Doc.has_extension("oa_concepts"):
            Doc.set_extension("oa_concepts", default=[])

    def __call__(self, doc):

        text: str = doc.text
        doc._.set("oa_concepts", get_oaconcepts(text,  text_lng="de"))

        return doc

    
