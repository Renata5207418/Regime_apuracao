import os
import json
import pandas as pd
import base64
import re
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from serpro_auth import obter_token_autenticacao
from dotenv import load_dotenv
from models import Requisicao, Base

# Carrega variáveis de ambiente de um arquivo .env
load_dotenv()

# URL do banco de dados (substitua pelo seu caminho de banco de dados ou URL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///SEU_CAMINHO/serpro_respostas.db")

# Configura a conexão com o banco de dados
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Caminho da planilha a ser processada (substitua pelo caminho correto da sua planilha)
caminho_planilha = r'SEU_CAMINHO/RegimeApuracao_lote_Padrão.xlsx'
print(f"[INFO] Tentando carregar a planilha: {caminho_planilha}")

# Verifica se a planilha existe no caminho especificado
if not os.path.exists(caminho_planilha):
    raise FileNotFoundError(f"[ERRO] Arquivo Excel não encontrado no caminho especificado: {caminho_planilha}")

# Carrega a planilha utilizando pandas
planilha = pd.read_excel(caminho_planilha)
print(f"[INFO] Planilha carregada com sucesso, total de linhas: {len(planilha)}")

# Define o diretório para salvar os arquivos de resposta (substitua pelo seu diretório desejado)
caminho_respostas = os.path.join(os.getcwd(), 'respostas')
if not os.path.exists(caminho_respostas):
    os.makedirs(caminho_respostas)
print(f"[INFO] Diretório para salvar respostas: {caminho_respostas}")


# Função que faz a requisição para a API do SERPRO
def fazer_requisicao_serpro(endpoint='/Declarar', method='POST', data=None):
    """
    Faz uma requisição ao endpoint da API do SERPRO para o serviço de opção de regime.
    """
    try:
        # Obtém o token de autenticação necessário para a requisição (substitua conforme sua lógica de autenticação)
        access_token, jwt_token = obter_token_autenticacao()
        print("[INFO] Token de autenticação obtido com sucesso.")
    except Exception as e:
        print(f"[ERRO] Erro ao obter o token de autenticação: {e}")
        return None, f"Erro ao obter token de autenticação: {e}"

    # Define a URL do endpoint da API
    url = f'https://gateway.apiserpro.serpro.gov.br/integra-contador/v1{endpoint}'

    # Define os cabeçalhos para a requisição
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'jwt_token': jwt_token
    }

    print(f"[INFO] Fazendo requisição para a URL: {url}")

    try:
        # Envia a requisição HTTP (POST por padrão)
        if method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            print("[ERRO] Método HTTP não suportado.")
            return None, "Método HTTP não suportado."

        print(f"[INFO] Status da resposta: {response.status_code}")

        # Verifica se a requisição foi bem-sucedida (status 200)
        if response.status_code == 200:
            response_data = response.json()
            print("[INFO] Requisição bem-sucedida. Processando resposta...")

            mensagens = response_data.get("mensagens", [])
            mensagem_texto = ", ".join(
                [f"{mensagem.get('codigo', '')}: {mensagem.get('texto', '')}" for mensagem in mensagens]
            )

            if response_data.get("dados"):
                try:
                    dados = json.loads(response_data["dados"])
                    return dados, mensagem_texto or None
                except ValueError as ve:
                    print(f"[ERRO] Erro ao processar campo 'dados' da resposta: {ve}")
                    return None, f"Erro ao processar 'dados': {ve}"

            return None, mensagem_texto or "Nenhum dado encontrado."

        else:
            # Caso a requisição não tenha sido bem-sucedida
            response_data = response.json()
            mensagem_erro = response_data.get("mensagens", [{"texto": "Erro desconhecido do servidor"}])
            mensagem_texto = ", ".join(
                [f"{mensagem.get('codigo', '')}: {mensagem.get('texto', '')}" for mensagem in mensagem_erro]
            )
            print(f"[ERRO] Requisição falhou. Status: {response.status_code} - Mensagem: {mensagem_texto}")
            return None, mensagem_texto

    except requests.RequestException as e:
        print(f"[ERRO] Erro durante a requisição: {e}")
        return None, f"Erro na requisição: {str(e)}"


# Função para remover caracteres não numéricos de um número de documento (CPF/CNPJ)
def formatar_numero_documento(numero):
    """
    Remove caracteres não numéricos do documento (CPF/CNPJ).
    """
    return re.sub(r'\D', '', numero)


# Função para montar o JSON necessário para solicitar a opção de regime de apuração
def montar_json_opcao_regime(numero_contribuinte, tipo_contribuinte, ano_opcao, tipo_regime, descritivo_regime):
    """
    Monta o JSON necessário para solicitar a opção de regime de apuração ao SERPRO.
    """
    json_dados = {
        "contratante": {
            "numero": "00000000000000",  # Substitua com o número cnpj do contratante
            "tipo": 2
        },
        "autorPedidoDados": {
            "numero": "00000000000000",  # Substitua com o número cnpj do autor
            "tipo": 2
        },
        "contribuinte": {
            "numero": numero_contribuinte,
            "tipo": tipo_contribuinte
        },
        "pedidoDados": {
            "idSistema": "REGIMEAPURACAO",
            "idServico": "EFETUAROPCAOREGIME101",
            "versaoSistema": "1.0",
            "dados": json.dumps({
                "anoOpcao": ano_opcao,
                "tipoRegime": tipo_regime,
                "descritivoRegime": descritivo_regime,
                "deAcordoResolucao": True
            }, ensure_ascii=False)
        }
    }
    print(f"[INFO] JSON montado para o contribuinte {numero_contribuinte}: {json.dumps(json_dados, indent=2)}")
    return json_dados


# Função para salvar o demonstrativo PDF gerado pela API
def salvar_resposta_em_arquivo(index, cnpj_matriz, demonstrativo_pdf_base64):
    """
    Salva o demonstrativo PDF em arquivos físicos, utilizando o CNPJ e índice como identificador.
    """
    try:
        # Define o caminho onde o PDF será salvo (substitua pelo seu diretório desejado)
        caminho_pdf = os.path.join(caminho_respostas, f'{cnpj_matriz}_demonstrativo_{index}.pdf')

        if demonstrativo_pdf_base64:
            # Salva o arquivo PDF após decodificá-lo de base64
            with open(caminho_pdf, 'wb') as pdf_file:
                pdf_file.write(base64.b64decode(demonstrativo_pdf_base64))
            print(f"[INFO] Arquivo PDF salvo com sucesso: {caminho_pdf}")

    except Exception as e:
        print(f"[ERRO] Erro ao salvar arquivos para o CNPJ {cnpj_matriz}: {e}")


# Função principal que processa a planilha e envia as requisições para a API
def processar_planilha_e_enviar_requisicoes(df):
    """
    Processa a planilha Excel, lendo linha por linha e enviando os dados para a API do SERPRO.
    """
    print("[INFO] Iniciando o processamento da planilha...")

    for index, row in df.iterrows():

        try:
            # Formata o número do CNPJ
            numero_contribuinte = formatar_numero_documento(str(row['CNPJ']))
            numero_contribuinte = numero_contribuinte.zfill(14)

            # Obtém os dados da linha da planilha
            ano_opcao = int(row['Ano da Opção'])
            tipo_regime = int(row['Tipo Regime'])
            descritivo_regime = str(row['Descritivo Regime'])

            # Determina o tipo de contribuinte (CNPJ ou CPF)
            tipo_contribuinte = 2 if len(numero_contribuinte) == 14 else 1
            print(f"[INFO] Processando linha {index + 1}/{len(df)}: Contribuinte {numero_contribuinte} "
                  f"(Tipo {tipo_contribuinte})")

            # Monta o JSON com os dados para a requisição
            json_dados = montar_json_opcao_regime(
                numero_contribuinte=numero_contribuinte,
                tipo_contribuinte=tipo_contribuinte,
                ano_opcao=ano_opcao,
                tipo_regime=tipo_regime,
                descritivo_regime=descritivo_regime
            )

            # Envia a requisição para a API do SERPRO
            dados_retorno, mensagem = fazer_requisicao_serpro(data=json_dados)

            if dados_retorno:
                print(f"[INFO] Requisição para linha {index + 1} bem-sucedida. Salvando dados no banco de dados.")
                # Salva os dados retornados no banco de dados
                requisicao = Requisicao(
                    cnpj_matriz=dados_retorno.get("cnpjMatriz"),
                    ano_calendario=dados_retorno.get("anoCalendario"),
                    regime_escolhido=dados_retorno.get("regimeEscolhido"),
                    data_hora_opcao=dados_retorno.get("dataHoraOpcao"),
                    demonstrativo_pdf_base64=dados_retorno.get("demonstrativoPdf"),
                )
                session.add(requisicao)
                session.commit()

                # Salva o PDF gerado no arquivo
                salvar_resposta_em_arquivo(
                    index=index,
                    cnpj_matriz=numero_contribuinte,
                    demonstrativo_pdf_base64=dados_retorno.get("demonstrativoPdf")
                )

                print(f"[INFO] Linha {index + 1}: Sucesso - Dados salvos no banco de dados e arquivos gerados.")

            else:
                print(f"[ERRO] Linha {index + 1}: Falha - {mensagem}")

        except Exception as e:
            print(f"[ERRO] Erro ao processar a linha {index + 1}: {e}")


# Inicia o processamento da planilha e envio das requisições
processar_planilha_e_enviar_requisicoes(planilha)
