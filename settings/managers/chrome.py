from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from func import config

def create_chrome():
    options = Options()
    service = Service(config('driver_path'))
    driver = webdriver.Chrome(service=service, options=options)
    return driver