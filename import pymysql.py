import pymysql
import tkinter as tk
from tkinter import ttk, messagebox

# UI 설정
root = tk.Tk()  # Tk 루트 창을 먼저 생성
root.title("Cosmetic Product Search")
root.geometry("1000x800")  # 기본 창 크기 설정

# 로그인 상태 변수
is_logged_in = tk.BooleanVar(value=False)  # 기본값: 로그인 상태 아님
email_logged_in = None  # 로그인된 사용자의 이메일 저장
user_name_logged_in = None  # 로그인된 사용자의 이름 저장

# 검색 모드 변수 (기본값: 브랜드/제품 검색)
search_mode = tk.StringVar(value="default")  # Tk 생성 후 초기화해야 함

# 성분 제외 체크박스 상태 변수
exclude_ingredient = tk.BooleanVar(value=False)  # 기본값: 제외 안 함

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

# 검색 함수
def search_products():
    if not is_logged_in.get():  # 로그인하지 않았으면 검색 불가
        messagebox.showwarning("로그인 필요", "검색 기능을 이용하려면 로그인이 필요합니다.")
        return

    search_term = entry_search.get()
    is_exclude = exclude_ingredient.get()

    # 검색어가 비어있으면 경고 메시지 표시
    if not search_term:
        messagebox.showwarning("Input Error", "검색어를 입력해주세요.")
        return

    conn = connect_to_db()
    if conn is None:
        return

    # 기본 검색 쿼리
    query = ""
    conditions = [f"%{search_term}%"]

    # 검색 모드에 따라 쿼리 변경
    if search_mode.get() == "default":  # 기본 모드 (브랜드 및 제품 이름 검색)
        query = """
        SELECT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
        FROM Products p
        LEFT JOIN Brands b ON p.brand_id = b.brand_id
        LEFT JOIN Categories c ON p.category_id = c.category_id
        WHERE p.name LIKE %s OR b.name LIKE %s
        """
        conditions.append(f"%{search_term}%")
    elif search_mode.get() == "category":  # 카테고리 검색 모드
        query = """
        SELECT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
        FROM Products p
        LEFT JOIN Brands b ON p.brand_id = b.brand_id
        LEFT JOIN Categories c ON p.category_id = c.category_id
        WHERE c.name LIKE %s
        """
    elif search_mode.get() == "ingredient":  # 성분 검색 모드
        if is_exclude:  # 성분 제외 검색
            query = """
            SELECT DISTINCT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
            FROM Products p
            LEFT JOIN Brands b ON p.brand_id = b.brand_id
            LEFT JOIN Categories c ON p.category_id = c.category_id
            LEFT JOIN Product_Ingredients pi ON p.product_id = pi.product_id
            LEFT JOIN Ingredients i ON pi.ingredient_id = i.ingredient_id
            WHERE p.product_id NOT IN (
                SELECT pi.product_id
                FROM Product_Ingredients pi
                JOIN Ingredients i ON pi.ingredient_id = i.ingredient_id
                WHERE i.name LIKE %s
            )
            """
        else:  # 성분 포함 검색
            query = """
            SELECT DISTINCT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
            FROM Products p
            LEFT JOIN Brands b ON p.brand_id = b.brand_id
            LEFT JOIN Categories c ON p.category_id = c.category_id
            LEFT JOIN Product_Ingredients pi ON p.product_id = pi.product_id
            LEFT JOIN Ingredients i ON pi.ingredient_id = i.ingredient_id
            WHERE i.name LIKE %s
            """

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(conditions))
            results = cursor.fetchall()

            # 검색 결과 테이블 초기화
            treeview_results.delete(*treeview_results.get_children())

            # 검색 결과 테이블 갱신
            for row in results:
                treeview_results.insert("", "end", values=row)

            conn.close()
    except pymysql.MySQLError as e:
        messagebox.showerror("Query Error", f"Error executing query: {e}")

# 검색 모드 변경 함수
def set_search_mode(mode):
    search_mode.set(mode)
    # 검색 모드 변경 시 입력 필드 초기화 및 안내 메시지 표시
    entry_search.delete(0, tk.END)
    if mode == "default":
        label_mode.config(text="모드: 기본 (브랜드/제품 검색)")
        checkbox_exclude.grid_remove()  # 성분 제외 체크박스 숨김
    elif mode == "category":
        label_mode.config(text="모드: 카테고리 검색")
        checkbox_exclude.grid_remove()  # 성분 제외 체크박스 숨김
    elif mode == "ingredient":
        label_mode.config(text="모드: 성분 검색")
        checkbox_exclude.grid()  # 성분 제외 체크박스 표시

# 로그인 창 생성 함수
def open_login_window():
    login_window = tk.Toplevel(root)
    login_window.title("로그인")
    login_window.geometry("300x200+700+100")  # 오른쪽 위 위치
    
    # 로그인 입력 필드
    tk.Label(login_window, text="이메일:").pack(pady=5)
    entry_email = tk.Entry(login_window, width=30)
    entry_email.pack(pady=5)
    
    tk.Label(login_window, text="비밀번호:").pack(pady=5)
    entry_password = tk.Entry(login_window, width=30, show="*")
    entry_password.pack(pady=5)

    # 로그인 버튼
    tk.Button(login_window, text="로그인", command=lambda: login(entry_email.get(), entry_password.get(), login_window)).pack(pady=10)

    # 회원가입 버튼
    tk.Button(login_window, text="회원가입", command=open_signup_window).pack(pady=5)

# 로그인 함수
def login(email, password, window):
    global email_logged_in, user_name_logged_in
    if not email or not password:
        messagebox.showwarning("로그인 실패", "이메일과 비밀번호를 입력해주세요.")
        return

    conn = connect_to_db()
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            query = "SELECT user_id, name FROM Users WHERE email = %s AND password = %s"
            cursor.execute(query, (email, password))
            result = cursor.fetchone()
            if result:
                is_logged_in.set(True)
                email_logged_in = email  # 로그인된 이메일 저장
                user_name_logged_in = result[1]  # 로그인된 유저 이름 저장
                window.destroy()
                update_login_button()  # 로그인 버튼 업데이트
                messagebox.showinfo("로그인 성공", f"{user_name_logged_in}님, 환영합니다!")
            else:
                messagebox.showerror("로그인 실패", "이메일 또는 비밀번호가 잘못되었습니다.")
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"로그인 중 오류가 발생했습니다: {e}")
    finally:
        conn.close()

# 로그인 버튼 업데이트 함수
def update_login_button():
    if is_logged_in.get():
        button_login.config(text=f"{user_name_logged_in}님", state="disabled")  # 로그인 버튼을 유저 이름으로 대체
    else:
        button_login.config(text="로그인", state="normal")  # 기본 로그인 버튼으로 복구

# 회원가입 창 생성 함수
def open_signup_window():
    signup_window = tk.Toplevel(root)
    signup_window.title("회원가입")
    signup_window.geometry("300x300+700+300")
    
    # 회원가입 입력 필드
    tk.Label(signup_window, text="이름:").pack(pady=5)
    entry_name = tk.Entry(signup_window, width=30)
    entry_name.pack(pady=5)
    
    tk.Label(signup_window, text="이메일:").pack(pady=5)
    entry_email = tk.Entry(signup_window, width=30)
    entry_email.pack(pady=5)
    
    tk.Label(signup_window, text="비밀번호:").pack(pady=5)
    entry_password = tk.Entry(signup_window, width=30, show="*")
    entry_password.pack(pady=5)

    tk.Label(signup_window, text="비밀번호 확인:").pack(pady=5)
    entry_password_confirm = tk.Entry(signup_window, width=30, show="*")
    entry_password_confirm.pack(pady=5)

    # 회원가입 버튼
    tk.Button(signup_window, text="회원가입 완료", command=lambda: signup(entry_name.get(), entry_email.get(), entry_password.get(), entry_password_confirm.get())).pack(pady=10)

# 회원가입 함수
def signup(name, email, password, password_confirm):
    if not name or not email or not password or not password_confirm:
        messagebox.showwarning("회원가입 실패", "모든 필드를 입력해주세요.")
        return
    
    if password != password_confirm:
        messagebox.showwarning("회원가입 실패", "비밀번호가 일치하지 않습니다.")
        return
    
    conn = connect_to_db()
    if conn is None:
        return
    
    try:
        with conn.cursor() as cursor:
            # Users 테이블에 데이터 삽입
            query = "INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, password))
            conn.commit()  # 데이터베이스 변경 사항 적용
            messagebox.showinfo("회원가입 성공", "회원가입이 완료되었습니다!")
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"회원가입 중 오류가 발생했습니다: {e}")
    finally:
        conn.close()

# 검색 입력 필드 및 체크박스
search_frame = tk.Frame(root)
search_frame.pack(pady=10)

entry_search = tk.Entry(search_frame, width=50, font=("Arial", 14))
entry_search.grid(row=0, column=0, padx=5)

checkbox_exclude = tk.Checkbutton(search_frame, text="성분 제외", variable=exclude_ingredient)
checkbox_exclude.grid(row=0, column=1, padx=5)
checkbox_exclude.grid_remove()  # 기본적으로 숨김

# 검색 모드 표시
label_mode = tk.Label(root, text="모드: 기본 (브랜드/제품 검색)", font=("Arial", 12))
label_mode.pack(pady=5)

# 검색 모드 버튼
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

button_default = tk.Button(frame_buttons, text="기본 검색 (브랜드/제품)", command=lambda: set_search_mode("default"))
button_default.grid(row=0, column=0, padx=5)

button_category = tk.Button(frame_buttons, text="카테고리 검색", command=lambda: set_search_mode("category"))
button_category.grid(row=0, column=1, padx=5)

button_ingredient = tk.Button(frame_buttons, text="성분 검색", command=lambda: set_search_mode("ingredient"))
button_ingredient.grid(row=0, column=2, padx=5)

# 로그인 버튼
button_login = tk.Button(root, text="로그인", command=open_login_window)
button_login.place(x=900, y=10)

# 검색 버튼
button_search = tk.Button(root, text="검색", command=search_products, font=("Arial", 12))
button_search.pack(pady=10)

# 결과 표시용 Treeview
columns = ("product_name", "brand_name", "category_name", "price")
treeview_results = ttk.Treeview(root, columns=columns, show="headings", height=20)
treeview_results.pack(pady=10, expand=True, fill=tk.BOTH)

# 각 컬럼의 헤더 설정
treeview_results.heading("product_name", text="제품 이름")
treeview_results.heading("brand_name", text="브랜드")
treeview_results.heading("category_name", text="카테고리")
treeview_results.heading("price", text="가격")

# 프로그램 실행 시 초기화
update_login_button()

# 실행
root.mainloop()
