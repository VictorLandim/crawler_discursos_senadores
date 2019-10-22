from pymongo import MongoClient
import pickle

from preprocessor import *

client = MongoClient('localhost', 27017)
db = client["discursoDB"]
discursos = db["discursos"]

discursos_raw = discursos.find({"Conteudo": {
    "$ne": ""
}})

discursos_list = []
discursos_ids = []

for disc in discursos_raw:
    text = disc["Conteudo"]
    discursos_list.append(text)

    text_id = str(disc["_id"])
    discursos_ids.append(text_id)

with open("discursos_raw.pickle", 'wb') as handle:
    pickle.dump(discursos_list, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open("discursos_ids.pickle", 'wb') as handle:
    pickle.dump(discursos_ids, handle, protocol=pickle.HIGHEST_PROTOCOL)
