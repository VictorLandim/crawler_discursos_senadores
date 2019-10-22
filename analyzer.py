from pymongo import MongoClient
from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamulticore import LdaMulticore


def main():
    client = MongoClient('localhost', 27017)
    db = client["discursoDB"]
    discursos = db["discursos"]

    # print(discursos.find()[0]['Conteudo'])

    corpus = []

    for disc in discursos.find():
        discurso_text = disc["Conteudo"]
        corpus.append(discurso_text)

    print(len(corpus))

    # Create a corpus from a list of texts
    common_dictionary = Dictionary(common_texts)

    common_corpus = [common_dictionary.doc2bow(text) for text in common_texts]

    # Train the model on the corpus.
    lda = LdaMulticore(common_corpus, num_topics=10)


if __name__ == '__main__':
    main()
