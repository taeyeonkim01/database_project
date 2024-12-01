from tkinter import messagebox
from database import connect_to_db

def login(email, password):
    conn = connect_to_db()
    if conn is None:
        return False, None

    try:
        with conn.cursor() as cursor:
            query = "SELECT user_id, name FROM Users WHERE email = %s AND password = %s"
            cursor.execute(query, (email, password))
            result = cursor.fetchone()
            if result:
                return True, result[1]
            else:
                return False, None
    except Exception as e:
        messagebox.showerror("Database Error", f"Error during login: {e}")
        return False, None
    finally:
        conn.close()


def signup(name, email, password):
    conn = connect_to_db()
    if conn is None:
        return False

    try:
        with conn.cursor() as cursor:
            query = "INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, password))
            conn.commit()
            return True
    except Exception as e:
        messagebox.showerror("Database Error", f"Error during signup: {e}")
        return False
    finally:
        conn.close()
