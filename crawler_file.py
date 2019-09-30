import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import time
from bs4 import BeautifulSoup


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


start_time = time.time()

senadores_success = []
senadores_fail = []

discursos_success = []
discursos_fail = []

url = "http://legis.senado.leg.br/dadosabertos/senador/lista/legislatura/49/56"
headers = {"Accept": "application/json"}

senadoresResponse = requests_retry_session().get(url, headers=headers, timeout=20)

senadoresList = json.loads(senadoresResponse.content)[
    "ListaParlamentarLegislatura"]["Parlamentares"]["Parlamentar"]

for senadorNum, senador in enumerate(senadoresList):
    # for senadorNum, senador in enumerate(senadoresList[221:]):
    senadorId = senador["IdentificacaoParlamentar"]["CodigoParlamentar"]

    senadorUrl = "http://legis.senado.leg.br/dadosabertos/senador/{}/discursos".format(
        senadorId)

    response = requests_retry_session().get(senadorUrl, headers=headers, timeout=20)
    responseJson = json.loads(response.content)[
        "DiscursosParlamentar"]

    if "Parlamentar" not in responseJson:
        print("-- Senador {}/{} #{} - sem discursos".format(senadorNum +
                                                            1, len(senadoresList), senadorId))
        senadores_fail.append(senadorId)
        continue
    else:
        senadores_success.append(senadorId)
        responseJson = responseJson["Parlamentar"]

    senadorMetadados = responseJson["IdentificacaoParlamentar"]
    discursosList = responseJson["Pronunciamentos"]["Pronunciamento"]

    if type(discursosList) is not list:
        discursosList = [discursosList]

    for discursoNum, discurso in enumerate(discursosList):
        discursoId = discurso["CodigoPronunciamento"]

        discursoUrl = discurso["UrlTexto"]

        jsonMetadados = json.loads('{}')
        jsonMetadados["IdentificacaoParlamentar"] = senadorMetadados
        jsonMetadados["IdentificacaoPronunciamento"] = discurso

        discursoFilename = "./discursos_data/{}_dis.txt".format(discursoId)
        metadadosFilename = "./discursos_data/{}_met.txt".format(discursoId)

        discursoResponse = requests_retry_session().get(
            discurso["UrlTexto"], headers=headers, timeout=20).content

        soup = BeautifulSoup(discursoResponse, "html.parser")

        soupResult = soup.select_one('div.texto-integral')

        if not soupResult:
            print("-- Senador {}/{} #{}, Discurso {}/{} #{} - inexistente".format(senadorNum + 1,
                                                                                  len(senadoresList), senadorId, discursoNum, len(discursosList) - 1, discursoId))

            discursos_fail.append(discursoId)
        else:
            print("-- Senador {}/{} #{}, Discurso {}/{} #{}".format(senadorNum + 1,
                                                                    len(senadoresList), senadorId, discursoNum, len(discursosList) - 1, discursoId))
            discursos_success.append(discursoId)

            discursoText = soupResult.get_text()

            with open(discursoFilename, 'w+', encoding="utf-8") as f:
                f.write(str(discursoText))

            with open(metadadosFilename, 'w+') as f:
                f.write(str(jsonMetadados))


elapsed_time = int(time.time() - start_time)

with open('./discursos_data/_report.txt', 'w+') as f:
    f.write("CRAWLER REPORT\n\n")

    f.write("Elapsed time: {:02d}:{:02d}:{:02d}\n\n".format(
        elapsed_time // 3600, (elapsed_time % 3600 // 60), elapsed_time % 60))

    f.write("== Senadores - total: {} ==\n".format(
        len(senadores_fail) + len(senadores_success)))
    f.write("Failed: {}\n".format(len(senadores_fail)))
    f.write(str(senadores_fail))
    f.write("\nSuccessful: {}\n".format(len(senadores_success)))
    f.write(str(senadores_success))

    f.write("\n\n== Discursos - total: {} ==\n".format(
        len(discursos_fail) + len(discursos_success)))
    f.write("Failed: {}\n".format(len(discursos_fail)))
    f.write(str(discursos_fail))
    f.write("\nSuccessful: {}\n".format(len(discursos_success)))
    f.write(str(discursos_success))
