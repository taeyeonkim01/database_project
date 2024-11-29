import pymysql
import tkinter as tk
from tkinter import ttk, messagebox

# UI 설정
root = tk.Tk()  # Tk 루트 창을 먼저 생성
root.title("Cosmetic Product Search")

# 검색 모드 변수 (기본값: 브랜드/제품 검색)
search_mode = tk.StringVar(value="default")  # Tk 생성 후 초기화해야 함

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
    search_term = entry_search.get()

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
        SELECT p.name AS product_name, b.name AS brand_name
        FROM Products p
        LEFT JOIN Brands b ON p.brand_id = b.brand_id
        WHERE p.name LIKE %s OR b.name LIKE %s
        """
        conditions.append(f"%{search_term}%")
    elif search_mode.get() == "category":  # 카테고리 검색 모드
        query = """
        SELECT p.name AS product_name, c.name AS category_name
        FROM Products p
        LEFT JOIN Categories c ON p.category_id = c.category_id
        WHERE c.name LIKE %s
        """
    elif search_mode.get() == "ingredient":  # 성분 검색 모드
        query = """
        SELECT p.name AS product_name, i.name AS ingredient_name
        FROM Products p
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
    elif mode == "category":
        label_mode.config(text="모드: 카테고리 검색")
    elif mode == "ingredient":
        label_mode.config(text="모드: 성분 검색")

# 검색 입력 필드
label_search = tk.Label(root, text="검색어 입력:")
label_search.pack(pady=10)

entry_search = tk.Entry(root, width=50)
entry_search.pack(pady=5)

# 검색 모드 표시
label_mode = tk.Label(root, text="모드: 기본 (브랜드/제품 검색)")
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

# 검색 버튼
button_search = tk.Button(root, text="검색", command=search_products)
button_search.pack(pady=10)

# 결과 표시용 Treeview
columns = ("product_name", "additional_info")
treeview_results = ttk.Treeview(root, columns=columns, show="headings", height=10)
treeview_results.pack(pady=10)

# 각 컬럼의 헤더 설정
treeview_results.heading("product_name", text="제품 이름")
treeview_results.heading("additional_info", text="추가 정보")

# 실행
root.mainloop()
