import pymysql
import tkinter as tk
from tkinter import ttk, messagebox

def connect_to_db():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='dongguk01',
            database='cosmeticsdb',
            charset='utf8mb4'
        )
        return conn
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error connecting to database: {e}")
        return None

def search_products():
    # 입력된 검색 조건 가져오기
    keyword = search_entry.get()
    conn = connect_to_db()
    if not conn:
        return
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 쿼리 실행 (제품 이름 또는 브랜드 검색)
        query = f"""
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
    

# Tkinter 창 생성
root = tk.Tk()
root.title("Cosmetics Platform")
root.geometry("800x600")

# 검색 입력 필드
search_label = tk.Label(root, text="Search Products:")
search_label.pack(pady=10)
search_entry = tk.Entry(root, width=50)
search_entry.pack(pady=10)

# 검색 버튼
search_button = tk.Button(root, text="Search", command=search_products)
search_button.pack(pady=10)

# 검색 결과 테이블
result_table = ttk.Treeview(root, columns=("Name", "Brand", "Category", "Price"), show="headings")
result_table.heading("Name", text="Name")
result_table.heading("Brand", text="Brand")
result_table.heading("Category", text="Category")
result_table.heading("Price", text="Price")
result_table.pack(pady=20, fill=tk.BOTH, expand=True)

# Tkinter 이벤트 루프 시작 (이 코드가 가장 마지막이어야 함)
root.mainloop()
