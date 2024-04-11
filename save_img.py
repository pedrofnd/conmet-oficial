from config import data_time, data_str, dest_folder_hoje, dest_folder_ontem, dpas, anterior, dict,arquivo_img , enviar_arquivo_slack
from config import slack_token, slack_channel
import numpy as np
import cv2

#Esse import cv2 precisa ter instalado com o seguinte comando, pip install opencv-python

# Variáveis
arquivos = []                # Lista para caminhos das imagens
modelos = list(dict.keys())  # Modelos de config.py

# Cria dicionario para gerar imagem final, baseado em dpas (delta passado)
for i in range(0, len(modelos)):
    modelo = modelos[i]
    model_name = f'{modelo.lower().replace(" ", "")}'
    if dpas == 1:
        if modelo == "NCEP - GEFS":
            elementos = ['0', '4', '20', '24', '40', '44']
        elif modelo == "NCEP - GFS":
            elementos = ['0', '4', '20', '24', '40', '44']
        elif modelo == "ECMWF - ENS":
            elementos = ['0', '4', '20', '24', '36', '40']
    elif dpas == 2:
        elementos = ['0', '8', '20', '28']
    elif dpas == 3:
        elementos = ['0', '12', '20', '32']
    elif dpas == 4:
        elementos = ['0', '16', '20', '36']
    for j in range(0, len(elementos)):  # Insere caminho da imagem na lista
        if(j%2 == 0):
            arquivos.append(dest_folder_hoje + rf'\{model_name}\elemento_{elementos[j]}_{data_str}_{model_name}.png')
        elif(j%2 == 1):
            arquivos.insert(len(arquivos)-1, dest_folder_ontem + rf'\{model_name}\elemento_{elementos[j]}_{anterior}_{model_name}.png')

print(arquivos) # Imprime lista de caminhos

# Leitura da lista de caminhos
for k in range(0, len(arquivos)):
    print("Iteração: ", k+1)

    # Carrega imagem. Plotar com matplotlib
    imagem = cv2.imread(arquivos[k])
    #plt.imshow(imagem)
    #plt.show()

    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)     # Gera imagem cinza.
    ret, thresh = cv2.threshold(imagem_cinza, 15, 255, 0)       # Separa zona de interesse das bordas
    contornos, hierarquia = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)    # Encontra contornos/bordas na imagem

    # contornos[0] é a lista de pixels com o contorno externo
    #print("P1: ", contornos[0][0])
    #print("P2: ", contornos[0][1])
    #print("P3: ", contornos[0][2])
    #print("P4: ", contornos[0][3])

    # Extrai tamanho da zona de interesse
    dimensao = contornos[0][2][0] - contornos[0][0][0]

    # Para visualizar contorno identificado:
    #cv2.drawContours(imagem, contornos, 0, (0, 255,0), 3)
    #plt.imshow(imagem)
    #plt.show()

    # Dimensoes da zona de interesse
    x = dimensao[0]
    y = dimensao[1]

    # Cria nova imagem em branco: múltiplo da imagem cortada + folga (em pixels)
    if k == 0:
        largura_final = int((x + 10) * len(arquivos)/3) - 10
        altura_final = int(y * 3) + 20
        imagem_final = np.zeros([altura_final, largura_final, 3])

    # Trecho para remover fundo preto: https://www.geeksforgeeks.org/image-processing-without-opencv-python/
    a, l, d = imagem.shape  # a: altura, l: largura imagem maior

    # Posicao inicial da zona de interesse
    x_base = int((l-x)/2)
    y_base = int((a-y)/2)

    cortada = np.zeros([y, x, 3])

    # Extrai zona de interesse da imagem completa
    for i in range(0, y):
        for j in range(0, x):
            cortada[i, j] = imagem[y_base + i, x_base + j]

    imagem = cortada
    #cv2.imwrite('cortada.png', imagem_pequena1)

    '''
    # Redefinir tamanho da imagem
    xnovo = int(x/2)
    ynovo = int(y/2)
    xscala = xnovo/(x-1)
    yscala = ynovo/(y-1)
    
    escalada = np.zeros([ynovo, xnovo, 3])
    
    for i in range(0, ynovo-1):
        for j in range(0, xnovo-1):
            escalada[i, j] = imagem[1 + int(i / yscala),
                                    1 + int(j / xscala)]
    
    imagem = escalada
    img.imsave('reduzida.png', imagem_pequena1);
    
    largura = xnovo
    altura = ynovo
    '''

    largura = x
    altura = y

    # Inserir imagem cortada na imagem final
    linha = int(k/(len(arquivos)/3))   # P/ 18 imagens: 6 por linha
    coluna = int(k%(len(arquivos)/3))  # p/ 12 imagens: 4 por linha

    for i in range(0, altura):
        for j in range(0, largura):
            imagem_final[linha*(altura+10) + i, coluna*(largura+10) + j] = imagem[i, j]

    cv2.imwrite(arquivo_img, imagem_final)


# Chame a função para enviar o arquivo para slack
enviar_arquivo_slack(slack_token, slack_channel, arquivo_img)


print("Completo.")
