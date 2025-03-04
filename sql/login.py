from sql.config import Model


class Authen(Model):
    def Checklogin(self,username,password):
        return self.post("account-tool/login",data={"username":username,"password":password})

