import spacy
spacy.load('en_core_web_sm')
from spacy.lang.en import English
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from configuration import conf
import os
from gensim import corpora
import pickle
# from gensim.models import TfidfModel
from nltk.stem import PorterStemmer
from obj.repo import get_repo_info


ps = PorterStemmer()

parser = English()
en_stop = set(nltk.corpus.stopwords.words('english'))
# en_stop.add('model')
# en_stop.add('propose')
# en_stop.add('paper')
# en_stop.add('method')
# en_stop.add('approach')
# en_stop.add('problem')
# en_stop.add('training')
# en_stop.add('learning')
# en_stop.add('train')
# en_stop.add('learn')
# en_stop.add('algorithm')
# en_stop.add('approach')
# en_stop.add('accuracy')
# en_stop.add('precision')
# en_stop.add('measure')


en_stop_lemmas = set()
for es in en_stop:
    en_stop_lemmas.add(ps.stem(es))


def tokenize(text):
    lda_tokens = list()
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens


def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)


def get_lemma3(word):
    return ps.stem(word)


def prepare_text_for_lda(text):
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 2]
    tokens = [get_lemma3(token) for token in tokens]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [token for token in tokens if token not in en_stop_lemmas]
    return tokens


def get_all_text():
    text_data = []
    # abs_path = os.path.join(conf.paper_abs_path(), 'abstracts')
    abs_path = os.path.join(conf.paper_pdf_path(), 'text')
    repo_info = get_repo_info(combine_star_events=True)
    for ri in repo_info:
        title = getattr(ri, 'title')
        conference = getattr(ri, 'conf')
        if ri.year <= 2014:
            continue
        if ri.language == '' or ri.language is None:
            continue
        if title in conf.excluded_papers:
            continue
        if conference is None or conference == '':
            continue
        paper_id = getattr(ri, 'paper_id')
        f_path = os.path.join(abs_path, str(paper_id)+'.txt')
        with open(f_path, 'r', encoding='ascii', errors='ignore') as f_obj:
            file_content = f_obj.read()
        tokens = prepare_text_for_lda(file_content)
        text_data.append(tokens)
    return text_data



if __name__ == '__main__':
    text_data = get_all_text()
    dictionary = corpora.Dictionary(text_data)
    corpus = [dictionary.doc2bow(text) for text in text_data]
    pickle.dump(corpus, open('corpus2.pkl', 'wb'))
    dictionary.save('dictionary2.gensim')
# model = TfidfModel(corpus)
# corpus = model[corpus]
# pickle.dump(corpus, open('corpus.pkl', 'wb'))
# dictionary.save('dictionary.gensim')












