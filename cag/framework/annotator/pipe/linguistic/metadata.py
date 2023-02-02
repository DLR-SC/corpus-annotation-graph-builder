import spacy

from spacy.language import Language
from spacy.tokens import Token, Span, Doc


def count_tokens_w_attr(doc, attr):
    return {doc.vocab[k].text: v for k, v in doc.count_by(attr).items()}


def get_content_pos(pos_tuple=("verb", "noun", "adjective", "adverb")):
    pos_labels = []
    for label in spacy.load("en_core_web_sm").get_pipe("tagger").labels:
        if spacy.explain(label).lower().startswith(pos_tuple):
            pos_labels.append(label)
    return pos_labels


@Language.component("descriptor")
def descriptor_function(doc):
    CONTENT_POS = get_content_pos()
    if not Doc.has_extension("num_token"):
        Doc.set_extension("num_token", default=0)
    if not Doc.has_extension("num_content_tokens"):
        Doc.set_extension("num_content_tokens", default=0)

    doc._.num_token = doc.__len__()
    doc._.num_content_tokens = len(
        [token for token in doc if token.tag_ in CONTENT_POS]
    )

    pos_count_dict = count_tokens_w_attr(doc, spacy.attrs["POS"])

    for pos_tag, count in pos_count_dict.items():
        pos_tag_name = "{}_{}".format("pos_num_", pos_tag)
        if not Doc.has_extension(pos_tag_name):
            Doc.set_extension(pos_tag_name, default=0)
        doc._.set(pos_tag_name, count)

    return doc
