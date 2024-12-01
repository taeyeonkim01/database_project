# search.py

from tkinter import messagebox
from database import connect_to_db

def search_products(search_term, search_mode, is_exclude, user_id=None, filter_name=None):
    """
    검색 모드에 따라 입력 조건을 처리하여 데이터베이스에서 검색 결과를 반환.
    필터를 적용하여 검색 결과를 제한할 수 있습니다.
    """
    conn = connect_to_db()
    if conn is None:
        return []

    query = ""
    conditions = []

    try:
        with conn.cursor() as cursor:
            if search_mode == "default":  # 기본 검색 모드
                query = """
                SELECT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
                FROM Products p
                LEFT JOIN Brands b ON p.brand_id = b.brand_id
                LEFT JOIN Categories c ON p.category_id = c.category_id
                WHERE p.name LIKE %s OR b.name LIKE %s
                """
                conditions = [f"%{search_term}%", f"%{search_term}%"]
            elif search_mode == "category":  # 카테고리 검색 모드
                query = """
                SELECT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
                FROM Products p
                LEFT JOIN Brands b ON p.brand_id = b.brand_id
                LEFT JOIN Categories c ON p.category_id = c.category_id
                WHERE c.name LIKE %s
                """
                conditions = [f"%{search_term}%"]
            elif search_mode == "ingredient":  # 성분 검색 모드
                if is_exclude:  # 성분 제외 검색
                    query = """
                    SELECT DISTINCT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
                    FROM Products p
                    LEFT JOIN Brands b ON p.brand_id = b.brand_id
                    LEFT JOIN Categories c ON p.category_id = c.category_id
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
                    JOIN Product_Ingredients pi ON p.product_id = pi.product_id
                    JOIN Ingredients i ON pi.ingredient_id = i.ingredient_id
                    LEFT JOIN Brands b ON p.brand_id = b.brand_id
                    LEFT JOIN Categories c ON p.category_id = c.category_id
                    WHERE i.name LIKE %s
                    """
                conditions = [f"%{search_term}%"]
            else:
                messagebox.showerror("Search Error", "지원하지 않는 검색 모드입니다.")
                return []

            # 사용자 필터 적용
            if user_id and filter_name:
                # 필터 ID 가져오기
                filter_query = "SELECT filter_id FROM User_Filters WHERE user_id = %s AND filter_name = %s"
                cursor.execute(filter_query, (user_id, filter_name))
                filter_result = cursor.fetchone()
                if not filter_result:
                    messagebox.showerror("Filter Error", "선택한 필터를 찾을 수 없습니다.")
                    return []
                filter_id = filter_result[0]

                # 포함 및 제외 성분 가져오기
                include_query = """
                SELECT i.ingredient_id
                FROM Filter_Ingredients fi
                JOIN Ingredients i ON fi.ingredient_id = i.ingredient_id
                WHERE fi.filter_id = %s AND fi.include_flag = TRUE
                """
                exclude_query = """
                SELECT i.ingredient_id
                FROM Filter_Ingredients fi
                JOIN Ingredients i ON fi.ingredient_id = i.ingredient_id
                WHERE fi.filter_id = %s AND fi.include_flag = FALSE
                """
                cursor.execute(include_query, (filter_id,))
                included_ingredients = [row[0] for row in cursor.fetchall()]

                cursor.execute(exclude_query, (filter_id,))
                excluded_ingredients = [row[0] for row in cursor.fetchall()]

                # 쿼리에 필터 적용
                if included_ingredients:
                    placeholders = ','.join(['%s'] * len(included_ingredients))
                    query += f"""
                    AND p.product_id IN (
                        SELECT pi.product_id
                        FROM Product_Ingredients pi
                        WHERE pi.ingredient_id IN ({placeholders})
                    )
                    """
                    conditions.extend(included_ingredients)

                if excluded_ingredients:
                    placeholders = ','.join(['%s'] * len(excluded_ingredients))
                    query += f"""
                    AND p.product_id NOT IN (
                        SELECT pi.product_id
                        FROM Product_Ingredients pi
                        WHERE pi.ingredient_id IN ({placeholders})
                    )
                    """
                    conditions.extend(excluded_ingredients)

            cursor.execute(query, tuple(conditions))
            results = cursor.fetchall()
            return results
    except Exception as e:
        messagebox.showerror("Query Error", f"Error executing query: {e}")
        return []
    finally:
        conn.close()
