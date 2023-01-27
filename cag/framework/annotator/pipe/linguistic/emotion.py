from statistics import mean

from simpletransformers.ner import NERModel
from spacy.language import Language
from spacy.tokens import Token, Span, Doc
import torch
from transformers import pipeline
from transformers.utils import logging
from nlpaf import logger
import pandas as pd
from nlpaf.util.timer import Timer
# REQUIRES sentencizer

@Language.factory("emotion_hartmann_component")
class EmotionHartmannFactory:
    _EMOTION_DOC_KEY: str = "emotions"
    _EMOTIONS = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]
    
    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar() # https://huggingface.co/docs/transformers/main/en/main_classes/logging#transformers.utils.logging.disable_default_handler
        logger.debug("init emotion_hartmann_component")

        self.transformer_nlp = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            truncation=True, top_k=None
        )
        logger.debug("initiated")

        if not Doc.has_extension("emotion_label"):
            Doc.set_extension("emotion_label", default=None)
        if not Doc.has_extension("emotions"):
            Doc.set_extension("emotions", default=None)

        for emotion in EmotionHartmannFactory._EMOTIONS:
            if not Span.has_extension(f"emotion_{emotion}"):
                Span.set_extension(f"emotion_{emotion}", default=None)
        if not Span.has_extension(f"emotion_dominant"):
            Span.set_extension(f"emotion_dominant", default=None)

    def __call__(self, doc):

        all_scores = {}
        for em in EmotionHartmannFactory._EMOTIONS:
            all_scores[em] = []

        sentence_lbls = []
        logger.debug("In the emotion pipe")

        for sentence in doc.sents:
            txt = sentence.text
            logger.debug("In the emotion pipe- looping over sentences")
            logger.debug(f"printing sent: {txt}")

            sent_emotion_result = self.transformer_nlp(txt)[0]
            logger.debug(f"sent_emotion_result {sent_emotion_result}")

            res_df = pd.DataFrame(sent_emotion_result)

            for sent_emotion_score in sent_emotion_result:
                label = sent_emotion_score['label']
                score = sent_emotion_score['score']

                all_scores[label].append(score)

                sentence._.set(f"emotion_{label}", score)
            dominant_lbl = res_df.iloc[res_df["score"].argmax()]["label"]
            sentence._.set(f"emotion_dominant", dominant_lbl)
            logger.debug(f"appending")
            sentence_lbls.append(dominant_lbl)

        doc_mean_df = pd.DataFrame(
            [{
                "label": x,
                "score_mean": mean(y) if len(y) > 0 else 0.0
            }
                for x, y in all_scores.items()]).set_index("label")

        doc_scores_df = pd.DataFrame([
            {
                "label": x,
                "count": sentence_lbls.count(x),
                "ratio": round(sentence_lbls.count(x) / len(sentence_lbls),5)
            }
            for x in set(sentence_lbls)
        ]).set_index("label")
        logger.debug(f"setting prediction")
        predictions_df = doc_scores_df.merge(doc_mean_df,
                                          how='outer',
                                          left_index=True,
                                          right_index=True)

        doc._.set("emotions", predictions_df.reset_index().to_dict('records'))
        doc._.set("emotion_label", predictions_df.reset_index().iloc[predictions_df["count"].argmax()]["label"])
        logger.debug("1 emotion call done")
        #all_.stop()
        return doc