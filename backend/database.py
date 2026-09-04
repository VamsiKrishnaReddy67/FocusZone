import mysql.connector


connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="5432",
    database="focuszone",
    port=3306
)

print("MySQL connected successfully!")

connection.close()