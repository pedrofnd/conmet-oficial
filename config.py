from datetime import datetime, timedelta
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


# Variáveis
url = 'https://www.conmetmeteorologia.com.br/accounts/login/'
login = 'Eneva'
senha = 'enevaconmet@082022'
path = os.path.abspath(os.path.dirname(__file__))
arquivo_img = 'imagem_final.jpg'

# Defina o token de acesso do Slack
slack_token = "xoxb-463567607316-5629112715858-8Z3umBiMNXoZPQGBVcEqj5IW"

# Defina o canal do Slack para enviar o arquivo
slack_channel = "##meteorologia"
#slack_channel = "##teste-integracao"

# Inserir data nos campos(OBS: Sempre deixar salvo aqui a data do próximo dia que será rodado o código)
ano = 2023
mes = 11
dia = 3
dfut = 1
dpas = 2

''' dfut (delta futuro): dias futuros que main2_v1.py salva
    dpas (delta passado): dias passados que save_img.py procura
    
    Operação normal: dfut e dpas = 1 (24h adiante) - O algoritmo lida com sexta e segunda.
    Feriado na ter/qua/qui: dfut = 2 (48h adiante)
                            dpas = 1 (24h anterior)
    Feriado na seg/sex: dfut = 4
                        dpas = 1 (se sexta) ou 4 (se segunda)
'''

data_time = datetime(ano, mes, dia)
data = data_time.strftime('%d/%m/%Y')
data_str = data_time.strftime('%Y-%m-%d')

folder = os.path.abspath(os.path.dirname(__file__))
dest_folder_hoje = os.path.join(folder, 'img','hoje')
dest_folder_ontem = os.path.join(folder, 'img','ontem')

# Check: atualizar dfut na sexta
if data_time.strftime('%A') == 'Friday' and dfut < 3:
    dfut = 3

# Cria dicionario para baixar imagens
dict = {'NCEP - GEFS': ['0', '20', '40'],
        'NCEP - GFS':  ['0', '20', '40'],
        'ECMWF - ENS': ['0', '20', '36']}

# Inserir elementos a partir de dfut
# Cada incremento de 4 nos elementos = +24h de previsoes
if dfut == 1:
    dict['NCEP - GEFS'].extend(['4', '24', '44'])
    dict['NCEP - GFS'].extend(['4', '24', '44'])
    dict['ECMWF - ENS'].extend(['4', '24', '40'])
elif dfut == 2:
    for i in dict:
        dict[i].extend(['8', '28'])
elif dfut == 3:
    for i in dict:
        dict[i].extend(['12', '32'])
elif dfut == 4:
    for i in dict:
        dict[i].extend(['16', '36'])

# Check: atualizar dpas na segunda:
if data_time.strftime('%A') == 'Monday' and dpas < 3:
    dpas = 3

# Gera data da captura dos arquivos da pasta \ontem com dpas
anterior = data_time - timedelta(dpas)
anterior = anterior.strftime('%Y-%m-%d')

print(list(dict.keys()))


def enviar_arquivo_slack(slack_token, slack_channel, arquivo_img):
    # Verifica se o arquivo existe
    if os.path.exists(arquivo_img):
        print(f"O arquivo {arquivo_img} existe.")
    else:
        print(f"O arquivo {arquivo_img} não existe.")
        return

    # Cria uma instância do WebClient usando o token do Slack
    client = WebClient(token=slack_token)

    try:
        # Faça o upload do arquivo para o Slack
        response = client.files_upload(
            channels=slack_channel,
            file=arquivo_img
        )

        # Exibe uma mensagem de confirmação
        print("O arquivo foi enviado para o Slack com sucesso!")

    except SlackApiError as e:
        # Exibe uma mensagem de erro caso ocorra algum problema
        print(f"Ocorreu um erro ao enviar o arquivo para o Slack: {e.response['error']}")