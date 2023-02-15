from typing import ClassVar
import pandas as pd
from simpletransformers.ner import NERModel, NERArgs
from spacy.language import Language
from spacy.tokens import Doc
from transformers.utils import logging
import nlpaf.utils as utils
from nlpaf.util.timer import Timer


@Language.factory("hedge_component")
class HedgeFactory:

    _METADATA_: ClassVar = "Hedge jeniakim/hedgehog HuggingFace"

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar()

        # ? HEDGEhog ?: BERT-based multi-class uncertainty cues recognition
        # https://huggingface.co/jeniakim/hedgehog
        ner_args = NERArgs()
        ner_args.silent = True
        self.model = NERModel(
            "bert",
            "jeniakim/hedgehog",
            use_cuda=False,
            labels=["C", "D", "E", "I", "N"],
            args=ner_args,
        )

        if not Doc.has_extension("hedge"):
            Doc.set_extension("hedge", default=None)

    def __call__(self, doc):
        logging.disable_progress_bar()
        results, _ = self.model.predict([doc.text])

        df_ = pd.DataFrame(
            {
                "words": [
                    list(x.keys())[0] for x in utils.flatten_list(results)
                ],
                "label": [
                    list(x.values())[0] for x in utils.flatten_list(results)
                ],
            }
        )

        labels_words = (
            df_.groupby(["label"], as_index=False)
            .agg({"words": ",".join})
            .set_index("label")
        )
        count_labels = (
            df_.groupby(["label"], as_index=False).size().set_index("label")
        )
        count_labels["ratio"] = round(
            count_labels["size"] / count_labels["size"].sum(), 3
        )

        predictions = (
            labels_words.merge(
                count_labels, how="outer", left_index=True, right_index=True
            )
            .reset_index()
            .to_dict("records")
        )

        doc._.set("hedge", predictions)

        return doc
