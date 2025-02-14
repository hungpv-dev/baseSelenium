from driver import Driver
from time import sleep

driver = Driver()
driver.get('https://facebook.com')
sleep(4)
driver.quit()
