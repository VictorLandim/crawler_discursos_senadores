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

client = MongoClient('localhost', 27017)
db = client["discursoDB"]
discursos = db["discursos"]

start_time = time.time()

# all_discursos = discursos.find()
# discursos_list = random.sample(list(all_discursos), 5000)

discursos_list = discursos.find(
    {"$and": [
        {"SiglaPartidoParlamentarNaData": {"$eq": "PT"}},
        {"Conteudo": {
            "$ne": ""
        }}
    ]})


# discursos_list = discursos.find()

text = []

for disc in discursos_list:
    text.append(disc["Conteudo"])

pipe = Pipeline([
    ('cleaning', Cleaner(max_word_lenght=4)),
    ('stopwords', StopWords(lang='portuguese', tokenize=True)),
    ('stemming', Stemmer(lang='portuguese', fit_reuse=True))])
pipe.fit(text)
res = pipe.transform(text)

# preproc = Preprocessor(max_word_lenght=2)
# preproc.fit(text)
# text = preproc.transform(text)

elapsed_time = time.time() - start_time
print(time.strftime("Discursos preprocessados, demorou %H:%M:%S:%m",
                    time.gmtime(elapsed_time)))


start_time = time.time()
# Create a corpus from a list of texts
data = [a.split() for a in res]

dictionary = Dictionary(data)

corpus = [dictionary.doc2bow(t) for t in data]

# os.environ['MALLET_HOME'] = 'X:\\Programs\\mallet\\mallet-2.0.8\\'
mallet_path = 'X:\\Programs\\mallet\\mallet-2.0.8\\bin\\mallet.bat'

# Train the model on the corpus.
lda = LdaMallet(mallet_path, corpus, id2word=dictionary, num_topics=10)
# lda = LdaModel(corpus, id2word=dictionary, num_topics=10, alpha='auto', eval_every=5, chunksize=10, passes=10, decay=0.9)

elapsed_time = time.time() - start_time
print(time.strftime("Lda model criado, demorou %H:%M:%S:%m", time.gmtime(elapsed_time)))

for index, topic in lda.show_topics(formatted=False, num_words=10):
    print('Topic: {} \nWords: {}'.format(
        index, [pipe.predict([w[0]])[0][0] for w in topic]))

# for index, topic in lda.show_topics(formatted=False, num_words=20):
#     print('Topic: {} \nWords: {}'.format(index, [w[0] for w in topic]))

model = malletmodel2ldamodel(lda)
vis = pyLDAvis.gensim.prepare(model, corpus, dictionary)


vis
pyLDAvis.save_html(vis, 'lda-pt-mallet.html')
