import gensim
from .prepare import prepare_text_for_lda
from gensim import corpora
import os


current_dir = os.path.dirname(__file__)
dictionary = corpora.Dictionary.load(os.path.join(current_dir, 'dictionary2.gensim'))
ldamodel = gensim.models.LdaModel.load(os.path.join(current_dir, 'model20.gensim'))


def get_lda_represent(text):
    tokens = prepare_text_for_lda(text)
    token_vector = dictionary.doc2bow(tokens)
    topic_vector = ldamodel[token_vector]
    return topic_vector





