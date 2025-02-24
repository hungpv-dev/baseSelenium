from sql.config import Model

class Proxies(Model):

    def __init__(self):
        super().__init__()
        self.table = 'proxies'
    
    def get_all(self ,params = None):
        return self.get(self.table,params=params)

    def create(self, data):
        return self.post(self.table, data=data)
    
    def update(self, id, data):
        return self.put(f"{self.table}/{id}", data=data)
    
    def show(self, id):
        return self.get(f"{self.table}/{id}")
    
    def destroy(self, id):
        return self.delete(f"{self.table}/{id}")
