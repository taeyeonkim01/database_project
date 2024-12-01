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
            SELECT p.product_id, p.name AS product_name, b.name AS brand_name, c.name AS category_name, p.price
            FROM Products p
            LEFT JOIN Brands b ON p.brand_id = b.brand_id
            LEFT JOIN Categories c ON p.category_id = c.category_id
            """
            where_conditions = []
            having_conditions = []
            parameters = []

            if search_mode == "default" and search_term:
                where_conditions.append("(p.name LIKE %s OR b.name LIKE %s)")
                parameters.extend([f"%{search_term}%", f"%{search_term}%"])
            elif search_mode == "category" and search_term:
                where_conditions.append("c.name LIKE %s")
                parameters.append(f"%{search_term}%")
            elif search_mode == "ingredient" and search_term:
                if is_exclude:
                    where_conditions.append("""
                    p.product_id NOT IN (
                        SELECT pi.product_id
                        FROM Product_Ingredients pi
                        JOIN Ingredients i ON pi.ingredient_id = i.ingredient_id
                        WHERE i.name LIKE %s
                    )
                    """)
                    parameters.append(f"%{search_term}%")
                else:
                    base_query += """
                    JOIN Product_Ingredients pi_search ON p.product_id = pi_search.product_id
                    JOIN Ingredients i_search ON pi_search.ingredient_id = i_search.ingredient_id
                    """
                    where_conditions.append("i_search.name LIKE %s")
                    parameters.append(f"%{search_term}%")
            elif search_mode == "filter_only" and user_id and filter_name:
                # 필터만으로 검색
                pass  # 아래에서 필터 조건 처리
            else:
                messagebox.showwarning("검색 오류", "유효한 검색어를 입력해주세요.")
                return []

            # 필터 적용
            if user_id and filter_name:
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

                include_ingredients = [row[0] for row in filter_ingredients if row[1]]  # include_flag가 True인 성분
                exclude_ingredients = [row[0] for row in filter_ingredients if not row[1]]  # include_flag가 False인 성분

                # 포함 성분 처리 (AND 연산)
                if include_ingredients:
                    num_includes = len(include_ingredients)
                    placeholders = ','.join(['%s'] * num_includes)
                    base_query += f"""
                    JOIN Product_Ingredients pi_inc ON p.product_id = pi_inc.product_id
                    """
                    where_conditions.append(f"pi_inc.ingredient_id IN ({placeholders})")
                    parameters.extend(include_ingredients)
                    # 각 제품이 모든 포함 성분을 포함하는지 확인
                    group_by = "GROUP BY p.product_id"
                    having_conditions.append(f"COUNT(DISTINCT pi_inc.ingredient_id) = {num_includes}")
                else:
                    group_by = ""
                # 제외 성분 처리
                if exclude_ingredients:
                    num_excludes = len(exclude_ingredients)
                    placeholders = ','.join(['%s'] * num_excludes)
                    where_conditions.append(f"""
                    p.product_id NOT IN (
                        SELECT pi_exc.product_id
                        FROM Product_Ingredients pi_exc
                        WHERE pi_exc.ingredient_id IN ({placeholders})
                    )
                    """)
                    parameters.extend(exclude_ingredients)
            else:
                group_by = ""

            # 최종 쿼리 구성
            final_query = base_query
            if where_conditions:
                final_query += " WHERE " + " AND ".join(where_conditions)
            if group_by:
                final_query += f" {group_by}"
            if having_conditions:
                final_query += " HAVING " + " AND ".join(having_conditions)

            cursor.execute(final_query, tuple(parameters))
            results = cursor.fetchall()
            return [row[1:] for row in results]  # product_id를 제외한 나머지 필드 반환
    except Exception as e:
        messagebox.showerror("Query Error", f"Error executing query: {e}")
        return []
    finally:
        conn.close()
