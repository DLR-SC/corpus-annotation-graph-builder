from pyArango.document import Document
from spacy.language import Language


@Language.component("preprocessor")
def preprocess_arango_doc(doc:Document):
    return (doc.text, {"_key": doc._key})



