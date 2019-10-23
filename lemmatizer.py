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

with open('discursos_raw.pickle', 'rb') as handle:
    discursos_raw = pickle.load(handle)

discursos_lemmatized = []

for i, disc in enumerate(discursos_raw):
    lemmatized = cogroo.lemmatize(disc)
    discursos_lemmatized.append(lemmatized)

    percentage = round(i*100/len(discursos_raw), 4)

    elapsed_time = time.time() - start_time
    time_str = time.strftime("%Hh %Mm %Ss",
                             time.gmtime(elapsed_time))

    print("Lemmatization progress: {}%, time: {}".format(percentage, time_str))

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

elapsed_time = time.time() - start_time
print(time.strftime("Discursos pre processados, lemmatizados e salvos, demorou %H:%M:%S:%m",
                    time.gmtime(elapsed_time)))
