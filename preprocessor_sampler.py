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

discurso_index = 74320

with open('discursos_raw.pickle', 'rb') as handle:
    discursos_raw = pickle.load(handle)


lemmatized = cogroo.lemmatize(discursos_raw[discurso_index])

stopword_list = list(
    STOP_WORDS) + list(nltk.corpus.stopwords.words('portuguese')) + ["sr", "sras", "exa", "exa.", "não", "nao"]

stopword_list = set(stopword_list)

pipe = Pipeline([
    ('cleaning', Cleaner(max_word_lenght=3)),
    ('stopwords', StopWords(lang='portuguese', stopword_list=stopword_list))])

pipe.fit([lemmatized])
discursos_processed = pipe.transform([lemmatized])

with open("RAW_SAMPLE.txt", 'w+') as f:
    f.write(discursos_raw[discurso_index])

with open("LEMMATIZED_SAMPLE.txt", 'w+') as f:
    f.write(lemmatized)

with open("PREPROC_SAMPLE.txt", 'w+') as f:
    f.write(discursos_processed[0])
