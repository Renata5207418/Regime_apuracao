import base64
import time
import logging
from requests_pkcs12 import post
from decouple import config
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

token_cache = {
    "access_token": None,
    "expires_in": None,
    "timestamp": None
}


def obter_token_autenticacao():
    """
    Obtém o token de autenticação do SERPRO.

    Esta função verifica se já existe um token em cache e se ele ainda é válido. Caso o token esteja expirado ou não
    exista, a função faz uma requisição ao endpoint de autenticação do SERPRO, utilizando um certificado digital e
    credenciais de acesso configuradas. O token obtido é armazenado em cache para ser reutilizado em futuras requisições
     evitando a necessidade de autenticação repetida.

    Retorna:
        tuple: Contém o `access_token` (token de autenticação) e o `jwt_token` (token JWT) obtidos da resposta da
        API do SERPRO.

    Exceções:
        Lança uma exceção caso ocorra algum erro durante o processo de autenticação, como falha na requisição
         ou erro no certificado.
    """

    if token_cache["access_token"] and token_cache["expires_in"] and token_cache["timestamp"]:
        tempo_passado = time.time() - token_cache["timestamp"]
        if tempo_passado < (token_cache["expires_in"] - 30):
            logging.info("Utilizando token em cache")
            return token_cache["access_token"], token_cache["jwt_token"]

    url = "https://autenticacao.sapi.serpro.gov.br/authenticate"
    caminho_certificado = config('CAMINHO_CERTIFICADO')
    certificado = f"{caminho_certificado}/{config('NOME_CERTIFICADO')}"
    senha_certificado = config('SENHA_CERTIFICADO')
    consumer_key = config('CONSUMER_KEY')
    consumer_secret = config('CONSUMER_SECRET')

    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{consumer_key}:{consumer_secret}".encode("utf8")).decode("utf8"),
        "Role-Type": "TERCEIROS",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    body = {'grant_type': 'client_credentials'}

    try:
        response = post(url, data=body, headers=headers, verify=True, pkcs12_filename=certificado,
                        pkcs12_password=senha_certificado)
        response.raise_for_status()

        response_data = response.json()
        token_cache["access_token"] = response_data.get("access_token")
        token_cache["jwt_token"] = response_data.get("jwt_token")
        token_cache["expires_in"] = response_data.get("expires_in")
        token_cache["timestamp"] = time.time()

        logging.info("Token obtido com sucesso")

        return token_cache["access_token"], token_cache["jwt_token"]

    except Exception as e:
        logging.error(f"Erro ao obter token de autenticação: {e}")
        raise Exception(f"Erro ao autenticar: {e}")
