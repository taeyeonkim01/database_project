import pymysql
import tkinter as tk
from tkinter import ttk, messagebox
import logging

# 로그 설정
logging.basicConfig(
    filename="debug.log",  # 디버깅 로그 파일 이름
    level=logging.DEBUG,  # 로그 레벨: DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 로그인 상태 플래그
is_logged_in = False  # 기본값: 로그인되지 않은 상태

# 데이터베이스 연결 함수
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

# 로그인 함수
def login_user():
    global is_logged_in
    email = email_entry.get()
    password = password_entry.get()

    # 디버깅 메시지
    print(f"DEBUG (login_user): Before login attempt, is_logged_in = {is_logged_in}", flush=True)
    logging.debug(f"DEBUG (login_user): Before login attempt, is_logged_in = {is_logged_in}")

    conn = connect_to_db()
    if not conn:
        return
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        query = "SELECT * FROM Users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        result = cursor.fetchone()

        if result:
            is_logged_in = True
            print(f"DEBUG (login_user): Login successful, is_logged_in = {is_logged_in}", flush=True)
            logging.debug(f"DEBUG (login_user): Login successful, is_logged_in = {is_logged_in}")
            messagebox.showinfo("Success", f"로그인 성공! 환영합니다, {result['name']}님!")
        else:
            is_logged_in = False
            print(f"DEBUG (login_user): Login failed, is_logged_in = {is_logged_in}", flush=True)
            logging.debug(f"DEBUG (login_user): Login failed, is_logged_in = {is_logged_in}")
            messagebox.showerror("Login Error", "이메일 또는 비밀번호가 올바르지 않습니다.")

    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error during login: {e}")
    finally:
        cursor.close()
        conn.close()

# 검색 기능
def search_products():
    global is_logged_in
    print(f"DEBUG (search_products): is_logged_in = {is_logged_in}", flush=True)
    logging.debug(f"DEBUG (search_products): is_logged_in = {is_logged_in}")

    if not is_logged_in:  # 로그인 상태 확인
        messagebox.showerror("Access Denied", "로그인 후 검색 기능을 사용할 수 있습니다.")
        return

    keyword = search_entry.get()
    conn = connect_to_db()
    if not conn:
        return
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        query = """
        SELECT name, brand, category, price
        FROM Products
        WHERE name LIKE %s OR brand LIKE %s
        """
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
        results = cursor.fetchall()

        # 기존 테이블 데이터 삭제
        for item in result_table.get_children():
            result_table.delete(item)

        # 결과를 테이블에 추가
        for row in results:
            result_table.insert("", "end", values=(row["name"], row["brand"], row["category"], row["price"]))
        
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error fetching data: {e}")
    finally:
        cursor.close()
        conn.close()

# 회원가입 창 열기
def open_register_window():
    register_window = tk.Toplevel(root)
    register_window.title("Register")
    register_window.geometry("400x300")

    name_label = tk.Label(register_window, text="Name:")
    name_label.pack(pady=5)
    name_entry = tk.Entry(register_window, width=40)
    name_entry.pack(pady=5)

    email_label = tk.Label(register_window, text="Email:")
    email_label.pack(pady=5)
    email_entry = tk.Entry(register_window, width=40)
    email_entry.pack(pady=5)

    password_label = tk.Label(register_window, text="Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(register_window, show="*", width=40)
    password_entry.pack(pady=5)

    def register_user():
        name = name_entry.get()
        email = email_entry.get()
        password = password_entry.get()

        if not name or not email or not password:
            messagebox.showerror("Input Error", "모든 필드를 입력하세요!")
            return

        conn = connect_to_db()
        if not conn:
            return
        cursor = conn.cursor()

        try:
            query_check = "SELECT COUNT(*) FROM Users WHERE email = %s"
            cursor.execute(query_check, (email,))
            result = cursor.fetchone()
            if result[0] > 0:
                messagebox.showerror("Duplicate Error", "이미 존재하는 이메일입니다. 다른 이메일을 사용하세요.")
                return

            query_insert = "INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query_insert, (name, email, password))
            conn.commit()
            messagebox.showinfo("Success", "사용자 가입이 완료되었습니다!")
            name_entry.delete(0, tk.END)
            email_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
        except pymysql.MySQLError as e:
            messagebox.showerror("Database Error", f"Error registering user: {e}")
        finally:
            cursor.close()
            conn.close()

    register_button = tk.Button(register_window, text="Register", command=register_user)
    register_button.pack(pady=20)

# Tkinter 창 생성
root = tk.Tk()
root.title("Cosmetics Platform")
root.geometry("1000x800")

# 검색 입력 필드
search_label = tk.Label(root, text="Search Products:")
search_label.pack(pady=10)
search_entry = tk.Entry(root, width=50)
search_entry.pack(pady=10)

search_button = tk.Button(root, text="Search", command=search_products)
search_button.pack(pady=10)

result_table = ttk.Treeview(root, columns=("Name", "Brand", "Category", "Price"), show="headings")
result_table.heading("Name", text="Name")
result_table.heading("Brand", text="Brand")
result_table.heading("Category", text="Category")
result_table.heading("Price", text="Price")
result_table.pack(pady=20, fill=tk.BOTH, expand=True)

# 로그인 입력 필드
email_label = tk.Label(root, text="Email:")
email_label.pack(pady=5)
email_entry = tk.Entry(root, width=40)
email_entry.pack(pady=5)

password_label = tk.Label(root, text="Password:")
password_label.pack(pady=5)
password_entry = tk.Entry(root, show="*", width=40)
password_entry.pack(pady=5)

login_button = tk.Button(root, text="Login", command=login_user)
login_button.pack(pady=10)

register_button = tk.Button(root, text="Register", command=open_register_window)
register_button.pack(pady=10)

root.mainloop()
