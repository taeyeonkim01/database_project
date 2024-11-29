import pymysql
import tkinter as tk
from tkinter import ttk, messagebox

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

# 카테고리, 성분 타입, 성분 이름을 데이터베이스에서 가져오는 함수
def fetch_filter_options():
    conn = connect_to_db()
    if conn is None:
        return [], [], []

    try:
        with conn.cursor() as cursor:
            # 카테고리 가져오기
            cursor.execute("SELECT name FROM Categories")
            categories = [row[0] for row in cursor.fetchall()]

            # 성분 타입 가져오기
            cursor.execute("SELECT name FROM Ingredient_Types")
            ingredient_types = [row[0] for row in cursor.fetchall()]

            # 성분 이름 가져오기
            cursor.execute("SELECT name FROM Ingredients")
            ingredients = [row[0] for row in cursor.fetchall()]

            conn.close()
            return categories, ingredient_types, ingredients
    except pymysql.MySQLError as e:
        messagebox.showerror("Query Error", f"Error executing query: {e}")
        return [], [], []

# 검색 함수
def search_products():
    search_term = entry_search.get()
    filters = {
        'category': category_filter_var.get(),
        'ingredient_type': ingredient_type_filter_var.get(),
        'ingredient_name': ingredient_name_filter_var.get()
    }

    # 검색어가 비어있으면 경고 메시지 표시
    if not search_term:
        messagebox.showwarning("Input Error", "검색어를 입력해주세요.")
        return

    conn = connect_to_db()
    if conn is None:
        return

    # 기본 검색 쿼리
    query = """
    SELECT p.name AS product_name, b.name AS brand_name, c.name AS category_name, 
           it.name AS ingredient_type, i.name AS ingredient_name 
    FROM Products p
    LEFT JOIN Brands b ON p.brand_id = b.brand_id
    LEFT JOIN Categories c ON p.category_id = c.category_id
    LEFT JOIN Product_Ingredients pi ON p.product_id = pi.product_id
    LEFT JOIN Ingredients i ON pi.ingredient_id = i.ingredient_id
    LEFT JOIN Ingredient_Types it ON i.type_id = it.type_id
    WHERE p.name LIKE %s OR b.name LIKE %s
    """

    conditions = [f"%{search_term}%", f"%{search_term}%"]

    # 필터가 설정되었으면 쿼리에 필터 조건 추가
    if filters['category'] and filters['category'] != "선택안함":
        query += " OR c.name LIKE %s"
        conditions.append(f"%{filters['category']}%")
    if filters['ingredient_type'] and filters['ingredient_type'] != "선택안함":
        query += " OR it.name LIKE %s"
        conditions.append(f"%{filters['ingredient_type']}%")
    if filters['ingredient_name'] and filters['ingredient_name'] != "선택안함":
        query += " OR i.name LIKE %s"
        conditions.append(f"%{filters['ingredient_name']}%")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(conditions))
            results = cursor.fetchall()

            # 검색 결과 테이블 갱신
            for row in results:
                treeview_results.insert("", "end", values=row)

            conn.close()
    except pymysql.MySQLError as e:
        messagebox.showerror("Query Error", f"Error executing query: {e}")

# UI 설정
root = tk.Tk()
root.title("Cosmetic Product Search")

# 검색 입력 필드
label_search = tk.Label(root, text="검색어 입력:")
label_search.pack(pady=10)

entry_search = tk.Entry(root, width=50)
entry_search.pack(pady=5)

# 필터 설정 (드롭다운 메뉴로 설정)
frame_filters = tk.Frame(root)
frame_filters.pack(pady=10)

category_filter_var = tk.StringVar()
ingredient_type_filter_var = tk.StringVar()
ingredient_name_filter_var = tk.StringVar()

# 기본값은 '선택안함'으로 설정
category_filter_var.set("선택안함")
ingredient_type_filter_var.set("선택안함")
ingredient_name_filter_var.set("선택안함")

# 카테고리 드롭다운 메뉴
category_filter_label = tk.Label(frame_filters, text="카테고리 필터:")
category_filter_label.grid(row=0, column=0, padx=5)
category_filter_dropdown = ttk.Combobox(frame_filters, textvariable=category_filter_var, width=20)
category_filter_dropdown.grid(row=0, column=1, padx=5)

# 성분 타입 드롭다운 메뉴
ingredient_type_filter_label = tk.Label(frame_filters, text="성분 타입 필터:")
ingredient_type_filter_label.grid(row=1, column=0, padx=5)
ingredient_type_filter_dropdown = ttk.Combobox(frame_filters, textvariable=ingredient_type_filter_var, width=20)
ingredient_type_filter_dropdown.grid(row=1, column=1, padx=5)

# 성분 이름 드롭다운 메뉴
ingredient_name_filter_label = tk.Label(frame_filters, text="성분 이름 필터:")
ingredient_name_filter_label.grid(row=2, column=0, padx=5)
ingredient_name_filter_dropdown = ttk.Combobox(frame_filters, textvariable=ingredient_name_filter_var, width=20)
ingredient_name_filter_dropdown.grid(row=2, column=1, padx=5)

# 검색 버튼
button_search = tk.Button(root, text="검색", command=search_products)
button_search.pack(pady=10)

# 결과 표시용 Treeview
columns = ("product_name", "brand_name", "category_name", "ingredient_type", "ingredient_name")
treeview_results = ttk.Treeview(root, columns=columns, show="headings", height=10)
treeview_results.pack(pady=10)

# 각 컬럼의 헤더 설정
for col in columns:
    treeview_results.heading(col, text=col.replace("_", " ").title())

# 드롭다운 메뉴 옵션을 설정하는 함수 호출
categories, ingredient_types, ingredients = fetch_filter_options()

# 드롭다운에 옵션 넣기
category_filter_dropdown['values'] = ["선택안함"] + categories
ingredient_type_filter_dropdown['values'] = ["선택안함"] + ingredient_types
ingredient_name_filter_dropdown['values'] = ["선택안함"] + ingredients

# 실행
root.mainloop()
