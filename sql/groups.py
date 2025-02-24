from sql.config import Model

class Group(Model):

    def __init__(self):
        super().__init__()
        self.table = 'groups'
    
    def get_all(self ,params = None):
        return self.get(self.table,params=params)

    def create(self, data):
        return self.post(self.table, data=data)
    
    def update(self, id, data):
        return self.put(f"{self.table}/{id}", data=data)
    
    def show(self, id):
        return self.get(f"{self.table}/{id}")
    
    def get_operasystem(self):
        return self.get(f"operating-systems")

    def destroy(self, id):
        return self.delete(f"{self.table}/{id}")
