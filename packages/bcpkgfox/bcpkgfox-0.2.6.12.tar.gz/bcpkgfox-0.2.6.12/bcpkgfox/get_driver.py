from .find_elements import find_element_with_wait_backcode, By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from typing import Optional

import undetected_chromedriver as uc

import random
import sys
import os

# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
#     return os.path.join(base_path, relative_path)

def backcode__dont_use__set_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

def backcode__dont_use__launch_browser(download_dir: str, extension_path, captcha_name, captcha_api_key) -> WebElement:
    global driver

    # Configurações para o Chrome
    options = uc.ChromeOptions()

    # Alterar o User-Agent
    options.add_argument(f"user-agent={backcode__dont_use__set_user_agent()}")

    # Default's
    profile = {
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'download.default_directory': download_dir,
    }
    options.add_experimental_option('prefs', profile)

    extensao_caminho = os.path.abspath(extension_path)

    # Configurações para reduzir detecção
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-infobars')

    if extension_path:
        options.add_argument(f'--load-extension={extensao_caminho}')

    # options.add_argument('--disable-extensions') # Fix: Possibilita ter extensões ou não, nunca influenciou na detecção

    # Inicializar o navegador com undetected_chromedriver
    driver = uc.Chrome(options=options, use_subprocess=True)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    cap_monster_names = ["capmonster", "captchamonster", "monster", "cap-monster", "captcha monster", "captcha-monster", "cmonter", "cap monster"]
    for name in cap_monster_names:
        if captcha_name.lower() == name:
            print("teste")
            backcode__dont_use__capmonster(captcha_api_key)

        print(f"{captcha_name.lower()} \\\ {name}")

    return driver

def backcode__dont_use__get(driver, link) -> WebElement:
    driver.get(link)

def backcode__dont_use__capmonster(api_key) -> None:
    global driver

    print("entrou")
    extension_id = "PABJFBCIAEDOMJJFELFAFEJKPPKNJLEH"

    driver.get(f"chrome-extension://{extension_id.lower()}/popup.html")

    find_element_with_wait_backcode(driver, By.ID, "client-key-input").send_keys(api_key)
    time.sleep(2.5)
    find_element_with_wait_backcode(driver, By.ID, "client-key-save-btn").click() # icone salvar
    print(" - Capmonter configurado.")