from .chrome import create_chrome
from func import config

managers = {
    'chrome': create_chrome,
}

def create_driver():
    browser = config('browser','chrome')
    driver = managers.get(browser)()
    return driver
