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
                user_info = {'user_id': result[0], 'name': result[1]}
                return True, user_info
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
            # 이메일 중복 확인
            cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
            if cursor.fetchone():
                messagebox.showwarning("회원가입 오류", "이미 사용 중인 이메일입니다.")
                return False

            query = "INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, password))
            conn.commit()
            return True
    except Exception as e:
        messagebox.showerror("Database Error", f"Error during signup: {e}")
        return False
    finally:
        conn.close()
