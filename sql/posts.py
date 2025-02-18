class Post:
    def __init__(self, connection):
        self.connection = connection

    def get(self):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM posts ORDER BY created_at DESC"
        cursor.execute(query)
        accounts = cursor.fetchall()
        return accounts

    def create(self, data):
        cursor = self.connection.cursor(dictionary=True)
        query = """
        INSERT INTO posts (account_id, fb_link, fb_id, created_at, updated_at) 
        VALUES (%s, %s, %s, NOW(), NOW())
        """
        cursor.execute(query, data)
        self.connection.commit()
        print("Account created successfully")


    def find(self, id):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM accounts WHERE id = %s"
        cursor.execute(query, (id,))
        account = cursor.fetchone()
        return account

    def update(self, id, data):
        cursor = self.connection.cursor()
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())
        values.append(id)
        query = f"UPDATE accounts SET {set_clause} WHERE id = %s"
        cursor.execute(query, values)
        self.connection.commit()
        print("Account updated successfully")

    def delete(self, username):
        cursor = self.connection.cursor()
        query = "DELETE FROM accounts WHERE username = %s"
        cursor.execute(query, (username,))
        self.connection.commit()
        print("Account deleted successfully")
