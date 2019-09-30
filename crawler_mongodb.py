import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient


def requests_retry_session(
    retries=5,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def crawl():

    client = MongoClient('localhost', 27017)
    db = client["discursoDB"]
    discursos = db["discursos"]

    start_time = time.time()

    url = "http://legis.senado.leg.br/dadosabertos/senador/lista/legislatura/49/56"
    headers = {"Accept": "application/json"}

    senadoresResponse = requests_retry_session().get(url, headers=headers, timeout=20)

    senadoresList = json.loads(senadoresResponse.content)[
        "ListaParlamentarLegislatura"]["Parlamentares"]["Parlamentar"]

    for senadorNum, senador in enumerate(senadoresList):
        senadorId = senador["IdentificacaoParlamentar"]["CodigoParlamentar"]

        senadorUrl = "http://legis.senado.leg.br/dadosabertos/senador/{}/discursos".format(
            senadorId)

        response = requests_retry_session().get(senadorUrl, headers=headers, timeout=20)
        responseJson = json.loads(response.content)["DiscursosParlamentar"]

        if "Parlamentar" not in responseJson:
            continue
        else:
            responseJson = responseJson["Parlamentar"]

        senadorMetadados = responseJson["IdentificacaoParlamentar"]

        discursosList = responseJson["Pronunciamentos"]["Pronunciamento"]

        if type(discursosList) is not list:
            discursosList = [discursosList]

        for discursoNum, discurso in enumerate(discursosList):
            discursoId = discurso["CodigoPronunciamento"]

            discursoUrl = discurso["UrlTexto"]

            discursoResponse = requests_retry_session().get(
                discurso["UrlTexto"], headers=headers, timeout=20).content

            soup = BeautifulSoup(discursoResponse, "html.parser")

            soupResult = soup.select_one('div.texto-integral')

            discursoTexto = ''

            if soupResult:
                discursoTexto = soupResult.get_text()

            discurso.pop('UrlTexto', None)
            discurso.pop('UrlTextoBinario', None)
            discurso["IdentificacaoParlamentar"] = senadorMetadados
            discurso["Conteudo"] = discursoTexto

            discursos.insert_one(discurso)
            print("-- Senador {}/{} #{}, Discurso {}/{} #{}".format(senadorNum + 1,
                                                                    len(senadoresList), senadorId, discursoNum, len(discursosList) - 1, discursoId))

    elapsed_time = int(time.time() - start_time)

    print("Elapsed time: {:02d}:{:02d}:{:02d}\n\n".format(
        elapsed_time // 3600, (elapsed_time % 3600 // 60), elapsed_time % 60))


if __name__ == '__main__':
    crawl()
