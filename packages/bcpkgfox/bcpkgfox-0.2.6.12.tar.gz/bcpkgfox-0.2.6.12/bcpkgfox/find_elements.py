from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import pyautogui
import time

def find_element_with_wait_backcode(driver, by, value, timeout, parent):
    if "css" in by:
        by = By.CSS_SELECTOR

    if parent is None:
        parent = driver  # Usa o driver principal se nenhum elemento pai for passado
    return WebDriverWait(parent, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def find_elements_with_wait_backcode(driver, by, value, timeout, parent):
    if "css" in by:
        by = By.CSS_SELECTOR

    if parent is None:
        parent = driver  # Usa o driver principal se nenhum elemento pai for passado
    return WebDriverWait(parent, timeout).until(
        EC.presence_of_all_elements_located((by, value))
    )

def move_to_image(imagens, click_on_final=False, tolerancia=1, timeout=10, repeat=False):
    """
    Move o mouse até o centro de uma imagem na tela e clica, se necessário.

    Args:
        imagens (list) : Caminho da imagem a ser localizada.
        click_on_final (bool): Se True, realiza um clique ao final.
        tolerancia (float): Tolerância para a comparação da imagem (opcional, valor padrão: 1).
        timeout (int): Tempo máximo (em segundos) para procurar a imagem antes de desistir (opcional, valor padrão: 10).
        repeat (bool): Se for True ele ignora o timeout, e fica tentando encontrar a imagem até conseguir, sem gerar erro

    Exemplo:
        caminho_imagem = 'C:\\User\\Caminho\\exemplo.png'
        move_to_image(caminho_imagem, click_on_final=True, tolerancia=0.9, timeout=30)

    Nota:
        Recomenda-se colocar a imagem na mesma pasta do arquivo MAIN para evitar problemas ao gerar o executável com pyinstaller e rodar em outras máquinas.
    """

    if isinstance(imagens, str):
        imagens = [imagens]

    attempts = 0
    ultima_excecao = None

    def funcao():
        nonlocal attempts, ultima_excecao
        try:
            # Os for's abaixo servem para caso seja mais de uma imagem
            for imagem in imagens:
                try:
                    localizacao = pyautogui.locateOnScreen(imagem, confidence=tolerancia)
                    break
                except:
                    localizacao = None
                    continue

            if localizacao is not None:
                x = localizacao.left + round(localizacao.width / 2)
                y = localizacao.top + round(localizacao.height / 2)
                pyautogui.moveTo(x, y)

                if click_on_final:
                    pyautogui.click()
                return localizacao

            else: raise FileNotFoundError()

        except Exception as e:
            attempts += 1
            ultima_excecao = e
            time.sleep(1)

    if repeat == True:
        while True:
            result = funcao()
            if result is not None:
                return result
    else:
        while attempts < timeout:
            result = funcao()
            if result is not None:
                return result

    # Se todas as tentativas falharem, levanta erro
    raise ValueError(f"Erro ao procurar a imagem '{imagens}' após 10 tentativas.") from ultima_excecao

def backcode__dont_use__wait_for(driver, object, type, timeout):
    # Encontra o objeto
    attempt = 0
    if timeout == 0:
        attempt = 2

    if type == "text":
        while attempt != timeout:
            if object in driver.page_source:
                return f"{object} encontrado"
            else:
                attempt += 1

    if type == "element":
        while attempt != timeout:
            try:
                element = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, object)))
                if element:
                    return f"{object} encontrado"
            except:
                attempt += 1

    if type == "image":
        while attempt != timeout:
            try:
                num_tolerancia = 1
                for _ in range(3):
                    try:
                        move_to_image(object, tolerancia=num_tolerancia, timeout=1)
                        return f"{object} encontrado"
                    except:
                        num_tolerancia -= 0.1
            except:
                attempt += 1

    raise ValueError(f"{object} não encontrado")

def backcode__dont_use__wait_for_d(driver, object, type, timeout):
    # Encontra o objeto
    attempt = 0
    if timeout == 0:
        attempt = float('inf')

    if type == "text":
        while attempt != timeout:
            if object in driver.page_source:

                # Depois de encontrar o elemento pela primeira vez espera ele sumir
                while object in driver.page_source \
                    and attempt != timeout:
                    time.sleep(1)
                    attempt += 1

                return f"{object} desapareceu"
            else:
                time.sleep(1)
                attempt += 1

    if type == "element":
        while attempt != timeout:
            try:
                element = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, object)))

                # Após encontrar umas primeira vez espera ele sumir
                WebDriverWait(driver, abs(timeout-attempt)).until(EC.invisibility_of_element_located((By.XPATH, object)))
                return f"{object} desapareceu"
            except:
                attempt += 1

    if type == "image":
        while attempt != timeout:
            try:

                # Vai abaixando a tolerancia até 0.8 para ver se encontra
                num_tolerancia = 1
                for _ in range(3):
                    try:
                        move_to_image(object, tolerancia=num_tolerancia, timeout=1)

                        # Após encontrar umas primeira vez espera ele sumir
                        while attempt != timeout:
                            try:
                                move_to_image(object, tolerancia=num_tolerancia, timeout=1)
                                time.sleep(0.9)
                            except:
                                return f"{object} desapareceu"

                    except:
                        num_tolerancia -= 0.1
            except:
                attempt += 1

    raise ValueError(f"{object} desapareceu")
