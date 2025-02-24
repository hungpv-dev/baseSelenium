from sql.config import Model

class Account(Model):
    
    def get_all(self ,params = None):
        return self.get(endpoint='accounts',params=params)
    
    def update(self, id, data):
        url = f"accounts/{id}"
        return self.put(url, data=data)
