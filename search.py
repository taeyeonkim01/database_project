from tkinter import messagebox
from database import connect_to_db

def search_products(search_term, search_mode, is_exclude):
    """
    검색 모드에 따라 입력 조건을 처리하여 데이터베이스에서 검색 결과를 반환.
    - 기본 검색 모드: 브랜드명 또는 제품명으로 검색.
    - 카테고리 검색 모드: 카테고리 이름으로 검색.
    - 성분 검색 모드: 성분 이름으로 검색 (포함/제외 설정 가능).
    """
    conn = connect_to_db()
    if conn is None:
        return []

    query = ""
    conditions = [f"%{search_term}%"]

    if search_mode == "default":  # 기본 검색 모드
        query = """
        SELECT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
        FROM Products p
        LEFT JOIN Brands b ON p.brand_id = b.brand_id
        LEFT JOIN Categories c ON p.category_id = c.category_id
        WHERE p.name LIKE %s OR b.name LIKE %s
        """
        conditions.append(f"%{search_term}%")  # 브랜드명도 포함
    elif search_mode == "category":  # 카테고리 검색 모드
        query = """
        SELECT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
        FROM Products p
        LEFT JOIN Brands b ON p.brand_id = b.brand_id
        LEFT JOIN Categories c ON p.category_id = c.category_id
        WHERE c.name LIKE %s
        """
    elif search_mode == "ingredient":  # 성분 검색 모드
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
            return results
    except Exception as e:
        messagebox.showerror("Query Error", f"Error executing query: {e}")
        return []
    finally:
        conn.close()
