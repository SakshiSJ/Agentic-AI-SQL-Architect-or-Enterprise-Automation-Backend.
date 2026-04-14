import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="172.31.26.116",
        user="tableau",
        password="P@ssW0rd#2",
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
