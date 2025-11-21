import os
import sys
import requests
import selenium as sl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


# webdriver configurations
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "excludeSwitches": ["enable-logging"],
    "profile.default_content_setting_values.automatic_downloads": 2,
    "download.default_directory": "/dev/null",  # Diretório inválido para impedir downloads
    "download.prompt_for_download": False,  # Bloqueia pop-ups de download
    "download.directory_upgrade": False,
    "download.extensions_to_open": "applications/docx",  # Apenas PDF pode abrir, docx fica bloqueado
    "plugins.always_open_pdf_externally": False,  # Impede que PDFs sejam baixados automaticamente
    "safebrowsing.enabled": False,  # Evita avisos de segurança sobre downloads
})


def get_atos():
    sys.stderr = open(os.devnull, 'w')

    chrome_options.add_argument(argument="--log-level=3")  # Suprime mensagens de INFO
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.ufpi.br/atos-e-spds")
    return driver


def get_month(year, p_text, a_text):
    year = int(year)
    
    if year >= 2017:
       return p_text.split(" - ")[1]
    elif year < 2017 and year > 2013:
        return p_text.split(" - ")[1].split(" ")[0]
    elif year == 2013 or year == 2012:
        return a_text.split(" ")[0]
    elif year <= 2011:
        return p_text.split(" - ")[1].split(" de ")[0]
    
    
if __name__ == "__main__":
    
    driver = get_atos()
    
    paragraphs_html = driver.find_elements(By.TAG_NAME, "p")[:-2]
    
    year = ""
    month = ""
    for p in paragraphs_html:
        
        try:
            a = p.find_element(By.TAG_NAME, "a")
            month = get_month(year, p.text, a.text)
            
            url_file = a.get_attribute("href")
            filename = f"{year}_{month}_ato.pdf"
            file_path = os.path.join("./atos", filename)

            response = requests.get(url_file)

            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
            else:
                print(f"Erro ao baixar arquivo {month}/{year}(status {response.status_code})")        

        except: 
            year = p.text