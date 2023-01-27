from statistics import mean

import pandas as pd
from spacy.language import Language
from spacy.tokens import  Span, Doc
from transformers.utils import logging
from transformers import pipeline
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from nlpaf.util.timer import Timer
from nlpaf import logger

# REQUIRES sentencizer
#https://huggingface.co/SkolkovoInstitute/roberta_toxicity_classifier?text=I+like+you.+I+love+you

@Language.factory("toxicity_component")
class ToxicityFactory:
    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        logging.disable_progress_bar()

        model_path = 'SkolkovoInstitute/roberta_toxicity_classifier'
        tokenizer = RobertaTokenizer.from_pretrained(model_path)
        model = RobertaForSequenceClassification.from_pretrained(model_path)

        self.transformer_nlp = pipeline('text-classification',
                                        model=model,
                                        tokenizer=tokenizer,
                                        truncation=True, top_k=None)

        if not Span.has_extension("toxicity_neutral"):
            Span.set_extension("toxicity_neutral", default=None)

        if not Span.has_extension("toxicity_toxic"):
            Span.set_extension("toxicity_toxic", default=None)

        if not Span.has_extension("toxicity_dominant"):
            Span.set_extension("toxicity_dominant", default=None)

        if not Doc.has_extension("toxicity"):
            Doc.set_extension("toxicity", default=None)
            
    def __call__(self, doc):
        #t = Timer("Toxicity")
        #t.start()
        all_scores = {}
        all_scores["neutral"] = []
        all_scores["toxic"] = []

        sentence_lbls = []
        logger.debug("in toxic")


        sent_toxicity_result_arr = self.transformer_nlp([sentence.text for sentence in doc.sents])
        for sent_toxicity_result in sent_toxicity_result_arr:
            #txt = sentence.text
            #sent_toxicity_result = self.transformer_nlp(txt)

            for sent_toxicity_score in sent_toxicity_result:
                label = sent_toxicity_score['label']
                score = sent_toxicity_score['score']

                all_scores[label].append(score)

                #sentence._.set(f"toxicity_{label}", score)
            sent_scores = pd.DataFrame(sent_toxicity_result)
            dominant_lbl = sent_scores.iloc[sent_scores["score"].argmax()]["label"]
            #sentence._.set(f"toxicity_dominant", dominant_lbl)
            sentence_lbls.append(dominant_lbl)


        doc_mean_df =  pd.DataFrame(
            [{
                "label":x,
                "score_mean":  mean(y) if len(y)>0 else 0.0}
            for x, y in all_scores.items() ]).set_index("label")


        doc_scores_df = pd.DataFrame([
            {
                "label":x,
                "count": sentence_lbls.count(x),
                "ratio":round(sentence_lbls.count(x)/len(sentence_lbls),3)
            }
            for x in set(sentence_lbls)
        ]).set_index("label")

        predictions = doc_scores_df.merge(doc_mean_df,
                                         how='outer',
                                         left_index=True,
                                         right_index=True).reset_index().to_dict('records')


        doc._.set("toxicity", predictions)
        #t.stop()
        logger.debug("in toxic - 1 run done")
        return doc