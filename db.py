import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host=127.0.0.1",
        user="your_username",
        password="YOUR_SECURE_PASSWORD",
        database="auto_bha_kal",
        port=3306
    )

def execute_sql(sql: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
