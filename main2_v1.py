from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import datetime
from selenium.webdriver.common.keys import Keys
import pyautogui
import os
from config import url, login, senha, data_time, data, data_str, dest_folder_hoje, dest_folder_ontem, path, dict
import os,io
import zipfile
import shutil
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests

#localizacao do chromedriver:
chrome_driver_path = os.path.join(path, "chromedriver", "chromedriver.exe")

#opcoes do chrome
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)
driver.maximize_window()
#movimento para abrir a url:
driver.get(url)

def digitar_lentamente(elemento, texto):
    for caractere in texto:
        elemento.send_keys(caractere)
        time.sleep(0.0001)

#colocando login e senha:
login_input = driver.find_element(By.XPATH, '//*[@id="id_login"]')
senha_input = driver.find_element(By.XPATH, '//*[@id="id_password"]')
digitar_lentamente(login_input, login)
digitar_lentamente(senha_input, senha)
#clique no botão para enviar login e senha
driver.find_element(By.XPATH, '//*[@id="content-wrap"]/main/div[2]/div/div/div/div/form/div[3]/div/button').click()

def select_model(modelo,data_str,path):

    # clicando no botao de comparar previsoes:
    driver.find_element(By.XPATH, '//*[@id="main_nav"]/ul/li[4]/a').click()

    # ajustando a data
    data_input = driver.find_element(By.XPATH, '//*[@id="date-prediction-1"]')
    if data_input is not None:
        data_input.clear()
        data_input.send_keys(data)
        data_input.send_keys(Keys.ENTER)
    else:
        print("Element not found")
    time.sleep(2)
    # clicando em qualquer lugar da tela para sair da data
    driver.find_element(By.XPATH, '//*[@id="div-frequency-1"]/label').click()

    #abre a listinha (clicar 2x pq tava dando problema)
    driver.find_element(By.XPATH, '//*[@id="select2-models-1-container"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="select2-models-1-container"]').click()
    time.sleep(2)
    #CLICA NO ECMWF
    time.sleep(2)
    driver.find_element(By.XPATH, f"//li[text()='{modelo}']").click()
    time.sleep(2)

    # selecionar opcao de rodada '00'
    select = Select(driver.find_element(By.ID,"initialization-1"))
    # Select the option with value "00"
    select.select_by_value("00")
    time.sleep(2)

    #opcao precipitacao acumulada 120 horas
    #abre a listinha (clicar 2x pq tava dando problema)
    driver.find_element(By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[5]/span/span[1]/span/span[2]').click()
    wait = WebDriverWait(driver, 5)
    #clica no menu de digitacao vazio para digitar o texto
    elemento = driver.find_element(By.XPATH, '/html/body/span/span/span[1]/input')
    texto = "Precipitação acumulada em 120 horas"
    time.sleep(1)
    elemento.click()
    wait = WebDriverWait(driver, 5)
    time.sleep(1)
    digitar_lentamente(elemento, texto)
    #apertar enter para selecionar o mapa correspondente
    elemento.send_keys(Keys.RETURN)

    #CLICA NO "BUSCAR"
    driver.find_element(By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[7]/button').click()
    time.sleep(5)

    print(modelo,"entrada")

    # Recebe lista de elementos por modelo
    if modelo == "NCEP - GEFS":
        elementos = dict['NCEP - GEFS']
        print(modelo,"americanos")
    elif modelo == "NCEP - GFS":
        elementos = dict['NCEP - GFS']
        print(modelo,"americanos")
    elif modelo == "ECMWF - ENS":
        elementos = dict['ECMWF - ENS']
        print(modelo, "europeu")
    else:
        print('nao encontrou os modelos')

    for elemento in elementos:
        print(elemento)
        #clicando no quadrado embaixo da imagem
        time.sleep(1)
        elemento_path = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="prediction-{elemento}"]')))
        elemento_path.click()
        #clicar na imagem para retirar o bug
        time.sleep(1)
        driver.find_element(By.XPATH, '/html/body/div[2]/div/main/div/div/div/div[3]/div/div/div[1]/img').click()
        time.sleep(1)
        #encontrando o id da imagem apos clicar na hora que quer
        element_img = driver.find_element(By.ID,'img-prediction-1')
        #obter o atributo src da imagem (ele eh mutavel)
        element_img_src = element_img.get_attribute('src')
        print(element_img_src)
        #salvando a imagem com o nome correto
        model_name = f'{modelo.lower().replace(" ", "")}'
        path_model = f'img\hoje\{model_name}\elemento_{elemento}_{data_str}_{model_name}.png'
        path_complete = os.path.join(path, path_model)
        print(path_complete)
        #print imagem
        driver.get(element_img_src)
        driver.save_screenshot(path_complete)
        #voltar a pagina
        time.sleep(1)
        driver.back()
        time.sleep(1)
    return

#remover todos os arquivos contidos dentro da estrutura: pasta/subpastas/(arquivos)
# Deletar o conteúdo da pasta de hoje e copiar para a pasta de ontem
def remove_files(pasta, pasta_destino):

    #deletar os itens da pasta ontem
    subpastas = os.listdir(pasta_destino)
    #subpastas dentro da pasta de hoje (pastas dos modelos)
    for subpasta in subpastas:
        #caminho completo da supbasta
        caminho_subpasta = os.path.join(pasta_destino, subpasta)
        #loop para os arquivos dentro da subpasta
        for nome_arquivo in os.listdir(caminho_subpasta):
            #caminho de cada arquivo
            caminho_arquivo = os.path.join(caminho_subpasta, nome_arquivo)
            #deletar o arquivo dentro da pasta / modelo/ arquivo
            os.remove(caminho_arquivo)
    #mover itens de hoje para ontem e limpar pasta hoje
    subpastas = os.listdir(pasta)
    #subpastas dentro da pasta de hoje (pastas dos modelos)
    for subpasta in subpastas:
        #caminho completo da supbasta
        caminho_subpasta = os.path.join(pasta, subpasta)
        print('dentro pasta', caminho_subpasta)
        #loop para os arquivos dentro da subpasta
        for nome_arquivo in os.listdir(caminho_subpasta):
            #caminho de cada arquivo
            caminho_arquivo = os.path.join(caminho_subpasta, nome_arquivo)
            print('dentro pasta', caminho_arquivo)
            # Copiar o arquivo para a pasta de destino
            destino_arquivo = os.path.join(pasta_destino, subpasta, nome_arquivo)
            shutil.copy(caminho_arquivo, destino_arquivo)
            #deletar o arquivo dentro da pasta / modelo/ arquivo
            os.remove(caminho_arquivo)



#usar a funcao remove_files para remanejar arquivos
remove_files(dest_folder_hoje, dest_folder_ontem)

#executar os modelos:
modelos = ["ECMWF - ENS", "NCEP - GFS", "NCEP - GEFS"]
for modelo in modelos:
    print("o modelo eh",modelo)
    select_model(modelo, data_str, path)

driver.close()