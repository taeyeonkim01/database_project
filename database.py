import pymysql
from tkinter import messagebox

def connect_to_db():
    try:
        conn = pymysql.connect(
            host='34.28.83.242',
            user='root',
            password='csc4020',
            database='cosmetic_db',
            charset='utf8mb4'
        )
        return conn
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error connecting to database: {e}")
        return None
