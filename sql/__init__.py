import mysql.connector
from mysql.connector import Error

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

# Example usage
connection = create_connection('localhost', 'root', '', 'spyad')
from .accounts import Account
from .posts import Post

accounts = Account(connection)
posts = Post(connection)