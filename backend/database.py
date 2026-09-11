import mysql.connector
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env from E:\FocusZone\.env
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    ssl_ca=os.path.join(BASE_DIR, "ca.pem")
)

print("Aiven MySQL connected successfully!")

connection.close()