from pymongo import MongoClient
from preprocessor import *
from cogroo_interface import Cogroo
from sklearn.pipeline import Pipeline
from spacy.lang.pt import STOP_WORDS
import nltk
import time
import pickle

from preprocessor import *

start_time = time.time()

cogroo = Cogroo.Instance()

client = MongoClient('localhost', 27017)
db = client["discursoDB"]
discursos = db["discursos"]

discursos_raw = discursos.find({"Conteudo": {
    "$ne": ""
}}, {"Conteudo": 1, "_id": 1})

# discursos_raw = discursos_raw[0:10]  # remove

discursos_list = []
discursos_ids = []

for disc in discursos_raw:
    text = disc["Conteudo"]
    discursos_list.append(text)

    text_id = str(disc["_id"])
    discursos_ids.append(text_id)

discursos_lemmatized = []

for disc in discursos_list:
    lemmatized = cogroo.lemmatize(disc)
    discursos_lemmatized.append(lemmatized)

stopword_list = list(
    STOP_WORDS) + list(nltk.corpus.stopwords.words('portuguese')) + ["sr", "sras", "exa", "exa.", "não", "nao"]

stopword_list = set(stopword_list)

pipe = Pipeline([
    ('cleaning', Cleaner(max_word_lenght=3)),
    ('stopwords', StopWords(lang='portuguese', stopword_list=stopword_list))])

pipe.fit(discursos_lemmatized)
discursos_processed = pipe.transform(discursos_lemmatized)

with open("discursos_lemma.pickle", 'wb') as handle:
    pickle.dump(discursos_processed, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open("discursos_lemma_ids.pickle", 'wb') as handle:
    pickle.dump(discursos_ids, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('discursos_lemma.pickle', 'rb') as handle:
#     b = pickle.load(handle)

elapsed_time = time.time() - start_time
print(time.strftime("Discursos pre processados, lemmatizados e salvos, demorou %H:%M:%S:%m",
                    time.gmtime(elapsed_time)))
