# search.py

from tkinter import messagebox
from database import connect_to_db

def search_products(search_term, search_mode, is_exclude, user_id=None, filter_name=None):
    """
    검색어와 필터를 사용하여 제품을 검색합니다.
    - search_term: 검색어 (None일 수 있음)
    - search_mode: 검색 모드 ("default", "category", "ingredient", "filter_only")
    - is_exclude: 성분 제외 여부 (bool)
    - user_id: 사용자 ID
    - filter_name: 적용할 필터 이름
    """
    conn = connect_to_db()
    if conn is None:
        return []

    try:
        with conn.cursor() as cursor:
            base_query = """
            SELECT DISTINCT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
            FROM Products p
            LEFT JOIN Brands b ON p.brand_id = b.brand_id
            LEFT JOIN Categories c ON p.category_id = c.category_id
            """
            conditions = []
            parameters = []

            if search_mode == "default" and search_term:
                conditions.append("(p.name LIKE %s OR b.name LIKE %s)")
                parameters.extend([f"%{search_term}%", f"%{search_term}%"])
            elif search_mode == "category" and search_term:
                conditions.append("c.name LIKE %s")
                parameters.append(f"%{search_term}%")
            elif search_mode == "ingredient" and search_term:
                if is_exclude:
                    conditions.append("""
                    p.product_id NOT IN (
                        SELECT pi.product_id
                        FROM Product_Ingredients pi
                        JOIN Ingredients i ON pi.ingredient_id = i.ingredient_id
                        WHERE i.name LIKE %s
                    )
                    """)
                else:
                    base_query += """
                    JOIN Product_Ingredients pi ON p.product_id = pi.product_id
                    JOIN Ingredients i ON pi.ingredient_id = i.ingredient_id
                    """
                    conditions.append("i.name LIKE %s")
                parameters.append(f"%{search_term}%")
            elif search_mode == "filter_only":
                pass  # 검색어 없이 필터만 사용
            else:
                messagebox.showwarning("검색 오류", "유효한 검색어를 입력해주세요.")
                return []

            # 필터 적용
            if user_id and filter_name:
                # 필터 ID 가져오기
                query = "SELECT filter_id FROM User_Filters WHERE user_id = %s AND filter_name = %s"
                cursor.execute(query, (user_id, filter_name))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("필터 오류", "선택한 필터를 찾을 수 없습니다.")
                    return []
                filter_id = result[0]

                # 포함 및 제외 성분 가져오기
                include_query = """
                SELECT ingredient_id FROM Filter_Ingredients WHERE filter_id = %s AND include_flag = TRUE
                """
                exclude_query = """
                SELECT ingredient_id FROM Filter_Ingredients WHERE filter_id = %s AND include_flag = FALSE
                """
                cursor.execute(include_query, (filter_id,))
                included_ingredients = [row[0] for row in cursor.fetchall()]

                cursor.execute(exclude_query, (filter_id,))
                excluded_ingredients = [row[0] for row in cursor.fetchall()]

                if included_ingredients:
                    placeholders = ','.join(['%s'] * len(included_ingredients))
                    base_query += f"""
                    JOIN Product_Ingredients pi_inc ON p.product_id = pi_inc.product_id
                    """
                    conditions.append(f"pi_inc.ingredient_id IN ({placeholders})")
                    parameters.extend(included_ingredients)

                if excluded_ingredients:
                    placeholders = ','.join(['%s'] * len(excluded_ingredients))
                    conditions.append(f"""
                    p.product_id NOT IN (
                        SELECT pi_exc.product_id
                        FROM Product_Ingredients pi_exc
                        WHERE pi_exc.ingredient_id IN ({placeholders})
                    )
                    """)
                    parameters.extend(excluded_ingredients)

            # 최종 쿼리 구성
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)

            cursor.execute(base_query, tuple(parameters))
            results = cursor.fetchall()
            return results
    except Exception as e:
        messagebox.showerror("Query Error", f"Error executing query: {e}")
        return []
    finally:
        conn.close()
