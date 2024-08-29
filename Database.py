#import pypyodbc as odbc
import mysql.connector

# Replace these with your database credentials
db_config = {
    "host": "bhissdw3dwp51x6heijv-mysql.services.clever-cloud.com",
    "user": "uxzduyvdtpeyj5ea",
    "password": "3QhVNyLKN8OOVuYcxY6R",
    "database": "bhissdw3dwp51x6heijv",
    # "Port":21480
}

# Establish the database connection
conn = None
cursor = None
try:
    conn = mysql.connector.connect(**db_config)
    print(conn)
    cursor = conn.cursor()
except Exception as e:
    print(e)


def reconnect():
    global conn, cursor
    try:
        conn.ping(reconnect=True)
    except:
        db_config = {
                "host": "bhissdw3dwp51x6heijv-mysql.services.clever-cloud.com",
                "user": "uxzduyvdtpeyj5ea",
                "password": "3QhVNyLKN8OOVuYcxY6R",
                "database": "bhissdw3dwp51x6heijv",
                }
                # Establish the database connection
        conn = mysql.connector.connect(**db_config) 
        cursor = conn.cursor()