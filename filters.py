# filters.py

from tkinter import messagebox
from database import connect_to_db

def get_user_filters(user_id):
    """
    해당 사용자의 필터 목록을 반환합니다.
    """
    conn = connect_to_db()
    if conn is None:
        return []

    try:
        with conn.cursor() as cursor:
            query = "SELECT filter_name FROM User_Filters WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            filters = [row[0] for row in results]
            return filters
    except Exception as e:
        messagebox.showerror("Database Error", f"Error fetching filters: {e}")
        return []
    finally:
        conn.close()

def create_filter(user_id, filter_name):
    """
    새로운 필터를 생성합니다.
    """
    conn = connect_to_db()
    if conn is None:
        return False

    try:
        with conn.cursor() as cursor:
            # 동일한 이름의 필터가 이미 있는지 확인
            query = "SELECT filter_id FROM User_Filters WHERE user_id = %s AND filter_name = %s"
            cursor.execute(query, (user_id, filter_name))
            result = cursor.fetchone()
            if result:
                messagebox.showwarning("필터 생성", "같은 이름의 필터가 이미 존재합니다.")
                return False

            # 새로운 필터 생성
            query = "INSERT INTO User_Filters (user_id, filter_name) VALUES (%s, %s)"
            cursor.execute(query, (user_id, filter_name))
            conn.commit()
            return True
    except Exception as e:
        messagebox.showerror("Database Error", f"Error during filter creation: {e}")
        return False
    finally:
        conn.close()

def delete_filter(user_id, filter_name):
    """
    필터를 삭제합니다.
    """
    conn = connect_to_db()
    if conn is None:
        return False

    try:
        with conn.cursor() as cursor:
            # 필터 ID 가져오기
            query = "SELECT filter_id FROM User_Filters WHERE user_id = %s AND filter_name = %s"
            cursor.execute(query, (user_id, filter_name))
            result = cursor.fetchone()
            if not result:
                messagebox.showwarning("필터 삭제", "해당 필터를 찾을 수 없습니다.")
                return False
            filter_id = result[0]

            # 필터에 연결된 성분 정보 삭제
            query = "DELETE FROM Filter_Ingredients WHERE filter_id = %s"
            cursor.execute(query, (filter_id,))

            # 필터 삭제
            query = "DELETE FROM User_Filters WHERE filter_id = %s"
            cursor.execute(query, (filter_id,))
            conn.commit()
            return True
    except Exception as e:
        messagebox.showerror("Database Error", f"Error during filter deletion: {e}")
        return False
    finally:
        conn.close()
