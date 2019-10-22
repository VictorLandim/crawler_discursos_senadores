from pymongo import MongoClient
from gensim.models.wrappers.ldamallet import malletmodel2ldamodel
from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
from gensim.models.wrappers import LdaMallet
from gensim.models import LdaModel
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import preprocess_documents
from sklearn.pipeline import Pipeline
import pyLDAvis.gensim
import time
import os
import random

from preprocessor import *

start_time = time.time()

f = open("discursos_all.txt", "r")
discursos_file = f.read()
f.close()

res = eval(discursos_file)

elapsed_time = time.time() - start_time
print(time.strftime("Discursos importados, demorou %H:%M:%S:%m",
                    time.gmtime(elapsed_time)))

start_time = time.time()

data = [a.split() for a in res]

dictionary = Dictionary(data)

corpus = [dictionary.doc2bow(t) for t in data]

mallet_path = 'X:\\Programs\\mallet\\mallet-2.0.8\\bin\\mallet.bat'

lda = LdaMallet(mallet_path, corpus=corpus, id2word=dictionary, num_topics=500)

elapsed_time = time.time() - start_time
print(time.strftime("Lda model criado, demorou %H:%M:%S:%m", time.gmtime(elapsed_time)))

with open("topics_500_latest.txt", 'w+') as f:
    for index, topic in lda.show_topics(formatted=False, num_words=15):
        f.write('[{}] - '.format(index))
        f.write(', '.join(str(line[0]) for line in topic))
        f.write('\n')
