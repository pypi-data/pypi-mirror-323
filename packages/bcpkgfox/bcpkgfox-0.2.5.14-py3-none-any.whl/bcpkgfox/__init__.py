from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from typing import Optional

from .find_elements import *
from .invoke_api import *
from .get_driver import *

import os

dirs_defaults = {
    "dir_kit": "C:\\TMPIMGKIT\\LAST_IMG",

    "dir_ggi": "C:\\TMPIMGGI\\LAST_IMG\\",
    "dir_gi": "C:\\TMPIMGI\\",

    "dir_robos": "C:\\TMP_ROBOS",

    "dir_pe": "C:\\TMPIMGPE\\"
}

dirs_sub = {
    "dir_consulta": "C:\\TMPIMGCONSULTA\\",
    "dir_GCPJ": "C:\\TMPIMGGCPJ\\"
    }

sub_pastas = ["FTP", "ftp2", "validacao"]


driver = None
By = By

def get_page_source():
    global driver
    return driver.page_source

def create_dirs(specifics_dirs: Optional[list] = None, disable_print_response: bool = False) -> str:
    """ Cria os diretórios padrões
     - Caso queira criar algum especifico passe em forma de LISTA o caminho deles.
     """
    global dirs
    dirs_created = []

    # Defaults
    for dir_ in dirs_defaults.values():

        if not os.path.exists(dir_):
            os.makedirs(dir_)
            dirs_created.append(dir_)

    # Sub's
    for dir_ in dirs_sub.values():
        for pasta in sub_pastas:

            if not os.path.exists(dir_):
                os.makedirs(os.path.join(dir_, pasta))
                dirs_created.append(os.path.join(dir_, pasta))

    # Specifics
    if specifics_dirs:
        for dir_ in specifics_dirs:
            if not os.path.exists(dir_):
                os.makedirs(os.path.join(dir_, pasta))
                dirs_created.append(os.path.join(dir_, pasta))

    # Log
    if disable_print_response == False:
        if dirs_created:
            print(f" -- {len(dirs_created)} pastas criadas:")
            for pasta in dirs_created:
                print(f" - {pasta}")

        else:
            print("Nenhum pasta para ser criada")

def initialize_driver():
    global driver
    if driver is None:
        driver = get_driver.backcode__dont_use__launch_browser(dir_dir)
        return driver

def finalize_driver():
    global driver

    driver.quit()
    driver = None
    return None

def get(link):
    global driver
    if driver != None:
        get_driver.backcode__dont_use__get(driver, link)

def find_element_with_wait(by, value, timeout=10, parent=None):
    global driver
    if driver != None:
        return find_elements.find_element_with_wait_backcode(driver, by.lower(), value, timeout, parent)

    else: raise ValueError("Error: Driver is None")

def find_elements_with_wait(by, value, timeout=10, parent=None):
    global driver
    if driver != None:
        return find_elements.find_elements_with_wait_backcode(driver, by.lower(), value, timeout, parent)

    else: raise ValueError("Error: Driver is None")

def wait_for_element_appear(object, type, timeout=10):
    """
    Aguarda até que um objeto (texto, elemento ou imagem) seja encontrado na tela.

    Args:
        object (str|list): O objeto a ser procurado. Pode ser um caminho de imagem, texto ou elemento XPATH.
        type (str): O tipo de objeto a ser procurado. Pode ser 'imagem', 'texto' ou 'elemento'.
        timeout (int): limite de tempo que vai procurar o objeto, coloque 0 para não ter limite

    Exemplo:
        wait_for('C:\\Caminho\\da\\imagem.png', 'imagem')
        wait_for('Texto a ser encontrado', 'texto')
        wait_for( XPATH_AQUI, 'elemento')
    """
    global driver
    tempo = timeout

    text_type = ['texto', 'string', 'palavra', 'mensagem', 'frase', 'conteúdo', 'texto_visível', 'texto_encontrado', 'texto_display', 'label']
    element_type = [ "element", "elemento", "botao", 'element', 'web_element', 'html_element', 'ui_element', 'interface_element', 'objeto', 'widget', 'campo', 'componente']
    imagem_type = [ 'imagem', 'img', 'imagem_png', 'imagem_jpeg', 'image', 'imagem_exata', 'padrão_imagem', 'foto', 'captura_tela', 'screenshot', 'imagem_visual']

    for escrita in text_type:
        if escrita in type.lower():
            type = "text"

    for escrita in element_type:
        if escrita in type.lower():
            type = "element"

    for escrita in imagem_type:
        if escrita in type.lower():
            type = "image"

    return find_elements.backcode__dont_use__wait_for(driver, object, type, timeout=tempo)

def wait_for_element_disappear(object, type, timeout=10):
    """
    Aguarda até que um objeto desapareça.(texto, elemento ou imagem)

    Args:
        object (str|list): O objeto a ser procurado. Pode ser um caminho de imagem, texto ou elemento XPATH.
        type (str): O tipo de objeto a ser procurado. Pode ser 'imagem', 'texto' ou 'elemento'.
        timeout (int): limite de tempo que vai procurar o objeto, coloque 0 para não ter limite

    Exemplo:
        wait_for('C:\\Caminho\\da\\imagem.png', 'imagem')
        wait_for('Texto a ser encontrado', 'texto')
        wait_for( XPATH_AQUI, 'elemento')
    """
    global driver
    tempo = timeout

    text_type = ['texto', 'string', 'palavra', 'mensagem', 'frase', 'conteúdo', 'texto_visível', 'texto_encontrado', 'texto_display', 'label']
    element_type = [ "element", "elemento", "botao", 'element', 'web_element', 'html_element', 'ui_element', 'interface_element', 'objeto', 'widget', 'campo', 'componente']
    imagem_type = [ 'imagem', 'img', 'imagem_png', 'imagem_jpeg', 'image', 'imagem_exata', 'padrão_imagem', 'foto', 'captura_tela', 'screenshot', 'imagem_visual']

    for escrita in text_type:
        if escrita in type.lower():
            type = "text"

    for escrita in element_type:
        if escrita in type.lower():
            type = "element"

    for escrita in imagem_type:
        if escrita in type.lower():
            type = "image"

    return find_elements.backcode__dont_use__wait_for_d(driver, object, type, timeout=tempo)

def selectfox(elemento, method, key):
    """
    Seleciona uma opção em um elemento <select>.

    - Parâmetros:
        - elemento: Elemento <select> encontrado pelo Selenium.
        - method: Método de seleção ('index', 'text' ou 'value').
        - key: Valor usado na seleção (índice, texto visível ou valor do atributo 'value').

    - Exemplo:
        elemento_select = bc.find_element_with_wait("xpath", '//select[@value="VALUE_DO_PRIMEIRO_SELECT"]')

        primeira_option = selectfox(elemento_select, "text", "TEXTO DO PRIMEIRO SELECT")
        primeira_option = selectfox(elemento_select, "value", "VALUE_DO_PRIMEIRO_SELECT")
        primeira_option = selectfox(elemento_select, "index", "0")

    """

    variations = {
        'index': ['index', 'indice', 'índice', 'posição', 'posição_na_lista', 'opção_numero', 'número_da_opção', 'opcao_indice', 'indice_da_opcao', 'numero_de_entrada'],
        'text': ['text', 'texto', 'texto_visível', 'conteúdo', 'frase', 'texto_exibido', 'palavra', 'mensagem', 'texto_na_página', 'texto_da_opcao'],
        'value': ['value', 'valor', 'valor_opcao', 'valor_da_opcao', 'valor_selecionado', 'value_opcao', 'valor_item', 'opcao_valor', 'item_valor', 'valor_atributo']
    }

    for key_method, values in variations.items():
        if method.lower() in map(str.lower, values):
            method = key_method
            break

    else:
        raise ValueError(f"Método '{method}' não é válido. Escolha entre 'index', 'text' ou 'value'.")

    select = Select(elemento)
    if method == "value":
        select.select_by_value(key)

    if method == "text":
        select.select_by_visible_text(key)

    if method == "index":
        select.select_by_index(key)
