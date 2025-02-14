from managers import create_driver

class Driver():
    def __init__(self):
        self.driver = create_driver()

    def get(self, url:str):
        self.driver.get(url)

    def quit(self):
        self.driver.quit()
        
    