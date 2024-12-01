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
            query = ""
            conditions = []
            parameters = []

            if search_mode == "default" and search_term:
                query = """
                SELECT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
                FROM Products p
                LEFT JOIN Brands b ON p.brand_id = b.brand_id
                LEFT JOIN Categories c ON p.category_id = c.category_id
                WHERE p.name LIKE %s OR b.name LIKE %s
                """
                parameters.extend([f"%{search_term}%", f"%{search_term}%"])
            elif search_mode == "category" and search_term:
                query = """
                SELECT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
                FROM Products p
                LEFT JOIN Brands b ON p.brand_id = b.brand_id
                LEFT JOIN Categories c ON p.category_id = c.category_id
                WHERE c.name LIKE %s
                """
                parameters.append(f"%{search_term}%")
            elif search_mode == "ingredient" and search_term:
                if is_exclude:
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
                    parameters.append(f"%{search_term}%")
                else:
                    query = """
                    SELECT DISTINCT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
                    FROM Products p
                    JOIN Product_Ingredients pi ON p.product_id = pi.product_id
                    JOIN Ingredients i ON pi.ingredient_id = i.ingredient_id
                    LEFT JOIN Brands b ON p.brand_id = b.brand_id
                    LEFT JOIN Categories c ON p.category_id = c.category_id
                    WHERE i.name LIKE %s
                    """
                    parameters.append(f"%{search_term}%")
            elif search_mode == "filter_only" and user_id and filter_name:
                # 필터만으로 검색
                query = """
                SELECT DISTINCT p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
                FROM Products p
                LEFT JOIN Brands b ON p.brand_id = b.brand_id
                LEFT JOIN Categories c ON p.category_id = c.category_id
                """
                filter_conditions = []
                filter_parameters = []

                # 필터 ID 가져오기
                cursor.execute("SELECT filter_id FROM User_Filters WHERE user_id = %s AND filter_name = %s", (user_id, filter_name))
                filter_result = cursor.fetchone()
                if not filter_result:
                    messagebox.showerror("필터 오류", "선택한 필터를 찾을 수 없습니다.")
                    return []
                filter_id = filter_result[0]

                # 포함 및 제외 성분 가져오기
                cursor.execute("""
                    SELECT ingredient_id, include_flag FROM Filter_Ingredients
                    WHERE filter_id = %s
                """, (filter_id,))
                filter_ingredients = cursor.fetchall()

                # 필터 조건 구성
                include_ingredients = [row[0] for row in filter_ingredients if row[1]]
                exclude_ingredients = [row[0] for row in filter_ingredients if not row[1]]

                if include_ingredients:
                    placeholders = ','.join(['%s'] * len(include_ingredients))
                    query += f"""
                    JOIN Product_Ingredients pi_inc ON p.product_id = pi_inc.product_id
                    """
                    filter_conditions.append(f"pi_inc.ingredient_id IN ({placeholders})")
                    filter_parameters.extend(include_ingredients)

                if exclude_ingredients:
                    placeholders = ','.join(['%s'] * len(exclude_ingredients))
                    filter_conditions.append(f"""
                    p.product_id NOT IN (
                        SELECT pi_exc.product_id
                        FROM Product_Ingredients pi_exc
                        WHERE pi_exc.ingredient_id IN ({placeholders})
                    )
                    """)
                    filter_parameters.extend(exclude_ingredients)

                if filter_conditions:
                    query += " WHERE " + " AND ".join(filter_conditions)
                parameters = filter_parameters
            else:
                messagebox.showwarning("검색 오류", "유효한 검색어를 입력해주세요.")
                return []

            # 선택된 필터가 있으면 추가 조건 적용 (filter_only 모드 제외)
            if filter_name and search_mode != "filter_only":
                cursor.execute("SELECT filter_id FROM User_Filters WHERE user_id = %s AND filter_name = %s", (user_id, filter_name))
                filter_result = cursor.fetchone()
                if filter_result:
                    filter_id = filter_result[0]
                    cursor.execute("""
                        SELECT ingredient_id, include_flag FROM Filter_Ingredients
                        WHERE filter_id = %s
                    """, (filter_id,))
                    filter_ingredients = cursor.fetchall()

                    include_ingredients = [row[0] for row in filter_ingredients if row[1]]
                    exclude_ingredients = [row[0] for row in filter_ingredients if not row[1]]

                    if include_ingredients:
                        placeholders = ','.join(['%s'] * len(include_ingredients))
                        query += f"""
                        JOIN Product_Ingredients pi_inc ON p.product_id = pi_inc.product_id
                        """
                        conditions.append(f"pi_inc.ingredient_id IN ({placeholders})")
                        parameters.extend(include_ingredients)

                    if exclude_ingredients:
                        placeholders = ','.join(['%s'] * len(exclude_ingredients))
                        conditions.append(f"""
                        p.product_id NOT IN (
                            SELECT pi_exc.product_id
                            FROM Product_Ingredients pi_exc
                            WHERE pi_exc.ingredient_id IN ({placeholders})
                        )
                        """)
                        parameters.extend(exclude_ingredients)

            # 최종 쿼리 구성
            if conditions:
                if 'WHERE' in query:
                    query += " AND " + " AND ".join(conditions)
                else:
                    query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, tuple(parameters))
            results = cursor.fetchall()
            return results
    except Exception as e:
        messagebox.showerror("Query Error", f"Error executing query: {e}")
        return []
    finally:
        conn.close()
