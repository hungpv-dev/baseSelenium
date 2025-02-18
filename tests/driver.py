from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from managers import create_chrome

# path = ChromeDriverManager().install()
# print(path)

driver = create_chrome()
driver.get('https://whatismyipaddess.com')
sleep(3)
driver.quit()