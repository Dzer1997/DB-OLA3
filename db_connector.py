# database_connection.py

import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        # Establish connection to the MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='',  # MySQL username
            password='',  # MySQL password
            database='final_assignment'  # Database name
        )
        if connection.is_connected():
            return connection
            
        else:
            raise Error("Failed to connect to the database.")
    except Error as e:
        print(f"Error: {e}")
        return None