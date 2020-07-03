import gensim
import pickle
from gensim import corpora


with open ('corpus2.pkl', 'rb') as f:
    corpus = pickle.load(f)
dictionary = corpora.Dictionary.load('dictionary2.gensim')

NUM_TOPICS = 20
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=NUM_TOPICS,
                                           id2word=dictionary, passes=30)

ldamodel.save('model20.gensim')
# ldamodel = gensim.models.ldamodel.LdaModel.load('model20.gensim')
topics = ldamodel.print_topics(num_words=10)
for topic in topics:
    print(topic)

