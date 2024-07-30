import time
import os
import random
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import subprocess
import converter

# Definir la lista de user agents y referers
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.67 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.0 Safari/537.36 Edg/93.0.934.0",
]

referers = [
    "https://www.google.com",
    "https://www.duckduckgo.com",
    "https://www.yahoo.com",
    "https://www.bing.com",
    "https://www.reddit.com",
    "https://www.wikipedia.org",
]

# Leer los símbolos desde el archivo
def read_symbols(file_path):
    with open(file_path, 'r') as file:
        symbols = [line.strip() for line in file.readlines()]
    random.shuffle(symbols)
    return symbols

# Obtener la ruta del directorio donde se encuentra el ejecutable o script
def get_base_path():
    if getattr(sys, 'frozen', False):
        # Si está congelado, usar la ruta del ejecutable
        return os.path.dirname(sys.executable)
    else:
        # Si no está congelado, usar la ruta del script
        return os.path.dirname(os.path.abspath(__file__))

# Definir la ruta del archivo de símbolos
base_path = get_base_path()
symbols_file_path = os.path.join(base_path, 'instrumentos.txt')

# Leer los símbolos desde el archivo
symbols = read_symbols(symbols_file_path)

# Crear una carpeta de descargas en la misma carpeta que el ejecutable si no existe
download_dir = os.path.join(base_path, 'descargas')
os.makedirs(download_dir, exist_ok=True)

def get_random_user_agent():
    return random.choice(user_agents)

def get_random_referer():
    return random.choice(referers)

def initialize_driver():
    chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument(f'user-agent={get_random_user_agent()}')
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    return uc.Chrome(options=chrome_options)

def smooth_scroll(driver):
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    scroll_step = random.randint(200, 400)
    current_position = 0
    while current_position < scroll_height:
        next_position = current_position + scroll_step
        driver.execute_script(f"window.scrollTo(0, {next_position});")
        time.sleep(random.uniform(0.3, 0.6))
        current_position = next_position

def process_symbol(symbol, driver):
    url = f"https://www.bolsadesantiago.com/resumen_instrumento/{symbol}"
    referer = get_random_referer()
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {"headers": {"Referer": referer}})
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Precios Históricos')]")))
    smooth_scroll(driver)
    try:
        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Precios Históricos')]")
        button.click()
        print(f"Botón 'Precios Históricos' encontrado y clickeado para {symbol}.")
        time.sleep(random.uniform(15, 30))
    except Exception as e:
        print(f"No se pudo encontrar o clickear el botón para {symbol}: {e}")

driver = initialize_driver()

for index, symbol in enumerate(symbols, start=1):
    try:
        process_symbol(symbol, driver)
    except Exception as e:
        print(f"Error al procesar el símbolo {symbol}: {e}")

    if index % 10 == 0:
        driver.quit()
        driver = initialize_driver()
        print("Navegador reiniciado después de procesar 10 símbolos.")

driver.quit()

print("Scrapping finalizado")

converter.main()