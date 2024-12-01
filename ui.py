import tkinter as tk
from tkinter import ttk, messagebox
from login import login
from search import search_products

class CosmeticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cosmetic Product Search")
        self.root.geometry("1000x800")

        self.is_logged_in = tk.BooleanVar(value=False)  # 로그인 상태
        self.user_name = None
        self.search_mode = tk.StringVar(value="default")  # 검색 모드 (기본값: default)
        self.exclude_ingredient = tk.BooleanVar(value=False)  # 성분 제외 체크

        self.create_widgets()

    def create_widgets(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)

        self.entry_search = tk.Entry(search_frame, width=50, font=("Arial", 14))
        self.entry_search.grid(row=0, column=0, padx=5)

        self.checkbox_exclude = tk.Checkbutton(search_frame, text="성분 제외", variable=self.exclude_ingredient)
        self.checkbox_exclude.grid(row=0, column=1, padx=5)
        self.checkbox_exclude.grid_remove()  # 기본적으로 체크박스를 숨김

        btn_search = tk.Button(search_frame, text="검색", command=self.handle_search, font=("Arial", 12))
        btn_search.grid(row=0, column=2, padx=5)

        self.label_mode = tk.Label(self.root, text="모드: 기본 (브랜드/제품 검색)", font=("Arial", 12))
        self.label_mode.pack(pady=5)

        self.create_mode_buttons()
        self.create_results_table()
        self.create_login_button()

    def create_mode_buttons(self):
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=10)

        btn_default = tk.Button(mode_frame, text="기본 검색", command=lambda: self.set_search_mode("default"))
        btn_default.grid(row=0, column=0, padx=5)

        btn_category = tk.Button(mode_frame, text="카테고리 검색", command=lambda: self.set_search_mode("category"))
        btn_category.grid(row=0, column=1, padx=5)

        btn_ingredient = tk.Button(mode_frame, text="성분 검색", command=lambda: self.set_search_mode("ingredient"))
        btn_ingredient.grid(row=0, column=2, padx=5)

    def create_results_table(self):
        columns = ("product_name", "brand_name", "category_name", "price")
        self.treeview_results = ttk.Treeview(self.root, columns=columns, show="headings", height=20)
        self.treeview_results.pack(pady=10, expand=True, fill=tk.BOTH)

        for col in columns:
            self.treeview_results.heading(col, text=col.replace("_", " ").capitalize())

    def create_login_button(self):
        self.button_login = tk.Button(self.root, text="로그인", command=self.open_login_window)
        self.button_login.place(x=900, y=10)

    def set_search_mode(self, mode):
        self.search_mode.set(mode)
        if mode == "default":
            self.label_mode.config(text="모드: 기본 (브랜드/제품 검색)")
            self.checkbox_exclude.grid_remove()
        elif mode == "category":
            self.label_mode.config(text="모드: 카테고리 검색")
            self.checkbox_exclude.grid_remove()
        elif mode == "ingredient":
            self.label_mode.config(text="모드: 성분 검색")
            self.checkbox_exclude.grid()

    def handle_search(self):
        if not self.is_logged_in.get():
            messagebox.showwarning("로그인 필요", "검색 기능을 이용하려면 로그인이 필요합니다.")
            return

        search_term = self.entry_search.get().strip()
        if not search_term:
            messagebox.showwarning("Input Error", "검색어를 입력해주세요.")
            return

        results = search_products(search_term, self.search_mode.get(), self.exclude_ingredient.get())
        self.treeview_results.delete(*self.treeview_results.get_children())
        for row in results:
            self.treeview_results.insert("", "end", values=row)

    def open_login_window(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("로그인")
        login_window.geometry("300x200")

        tk.Label(login_window, text="이메일:").pack(pady=5)
        entry_email = tk.Entry(login_window, width=30)
        entry_email.pack(pady=5)

        tk.Label(login_window, text="비밀번호:").pack(pady=5)
        entry_password = tk.Entry(login_window, width=30, show="*")
        entry_password.pack(pady=5)

        tk.Button(login_window, text="로그인", command=lambda: self.handle_login(entry_email.get(), entry_password.get(), login_window)).pack(pady=10)

    def handle_login(self, email, password, login_window):
        success, user_name = login(email, password)
        if success:
            self.is_logged_in.set(True)
            self.user_name = user_name
            login_window.destroy()
            self.button_login.config(text=f"{user_name}님")
            messagebox.showinfo("로그인 성공", f"환영합니다, {user_name}님!")
        else:
            messagebox.showerror("로그인 실패", "이메일 또는 비밀번호가 잘못되었습니다.")
