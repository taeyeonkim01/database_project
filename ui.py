# ui.py

import tkinter as tk
from tkinter import ttk, messagebox
from login import login
from search import search_products
from filters import get_user_filters, create_filter, delete_filter

class CosmeticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cosmetic Product Search")
        self.root.geometry("1000x800")

        self.is_logged_in = tk.BooleanVar(value=False)
        self.user_name = None
        self.user_id = None
        self.search_mode = tk.StringVar(value="default")
        self.exclude_ingredient = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        # 로그인 영역 생성
        self.create_login_area()

        # 필터 목록 영역 생성
        self.create_filter_list()

        # 검색 영역 생성
        self.create_search_area()

        # 모드 버튼 생성
        self.create_mode_buttons()

        # 결과 테이블 생성
        self.create_results_table()

    def create_login_area(self):
        login_frame = tk.Frame(self.root)
        login_frame.pack(anchor='nw', padx=10, pady=10)

        self.label_welcome = tk.Label(login_frame, text="로그인해주세요.", font=("Arial", 12))
        self.label_welcome.grid(row=0, column=0, columnspan=2, pady=5)

        tk.Label(login_frame, text="이메일:").grid(row=1, column=0, sticky='e', pady=2)
        self.entry_email = tk.Entry(login_frame, width=30)
        self.entry_email.grid(row=1, column=1, pady=2)

        tk.Label(login_frame, text="비밀번호:").grid(row=2, column=0, sticky='e', pady=2)
        self.entry_password = tk.Entry(login_frame, width=30, show="*")
        self.entry_password.grid(row=2, column=1, pady=2)

        self.button_login = tk.Button(login_frame, text="로그인", command=self.handle_login)
        self.button_login.grid(row=3, column=0, columnspan=2, pady=10)

    def create_filter_list(self):
        self.filter_frame = tk.Frame(self.root)
        self.filter_frame.pack(anchor='nw', padx=10, pady=10)

        self.label_filters = tk.Label(self.filter_frame, text="사용자 필터 목록:", font=("Arial", 12))
        self.label_filters.pack()

        self.listbox_filters = tk.Listbox(self.filter_frame, width=50, height=5)
        self.listbox_filters.pack(pady=5)

        button_frame = tk.Frame(self.filter_frame)
        button_frame.pack(pady=5)

        self.button_create_filter = tk.Button(button_frame, text="필터 생성", command=self.open_create_filter_window)
        self.button_create_filter.grid(row=0, column=0, padx=5)

        self.button_delete_filter = tk.Button(button_frame, text="필터 삭제", command=self.handle_delete_filter)
        self.button_delete_filter.grid(row=0, column=1, padx=5)

        # 초기에는 필터 관련 위젯을 비활성화
        self.toggle_filter_widgets(state='disabled')

    def create_search_area(self):
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

    def toggle_filter_widgets(self, state='normal'):
        widgets = [self.listbox_filters, self.button_create_filter, self.button_delete_filter]
        for widget in widgets:
            widget.config(state=state)

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

        # 선택된 필터 가져오기
        selected_filter = None
        if self.listbox_filters.curselection():
            index = self.listbox_filters.curselection()[0]
            selected_filter = self.listbox_filters.get(index)

        results = search_products(
            search_term,
            self.search_mode.get(),
            self.exclude_ingredient.get(),
            user_id=self.user_id,
            filter_name=selected_filter
        )
        self.treeview_results.delete(*self.treeview_results.get_children())
        for row in results:
            self.treeview_results.insert("", "end", values=row)

    def handle_login(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        success, user_info = login(email, password)
        if success:
            self.is_logged_in.set(True)
            self.user_name = user_info['name']
            self.user_id = user_info['user_id']
            self.label_welcome.config(text=f"환영합니다, {self.user_name}님!")
            self.entry_email.grid_remove()
            self.entry_password.grid_remove()
            self.button_login.grid_remove()
            self.toggle_filter_widgets(state='normal')
            self.refresh_filter_list()
        else:
            messagebox.showerror("로그인 실패", "이메일 또는 비밀번호가 잘못되었습니다.")

    def refresh_filter_list(self):
        self.listbox_filters.delete(0, tk.END)
        filters = get_user_filters(self.user_id)
        for filter_name in filters:
            self.listbox_filters.insert(tk.END, filter_name)

    def open_create_filter_window(self):
        create_filter_window = tk.Toplevel(self.root)
        create_filter_window.title("필터 생성")
        create_filter_window.geometry("300x200")

        tk.Label(create_filter_window, text="필터 이름:").pack(pady=5)
        entry_filter_name = tk.Entry(create_filter_window, width=30)
        entry_filter_name.pack(pady=5)

        tk.Button(
            create_filter_window,
            text="생성",
            command=lambda: self.handle_create_filter(entry_filter_name.get(), create_filter_window)
        ).pack(pady=10)

    def handle_create_filter(self, filter_name, window):
        if not filter_name:
            messagebox.showwarning("Input Error", "필터 이름을 입력해주세요.")
            return
        success = create_filter(self.user_id, filter_name)
        if success:
            messagebox.showinfo("필터 생성", "필터가 성공적으로 생성되었습니다.")
            window.destroy()
            self.refresh_filter_list()
        else:
            messagebox.showerror("필터 생성 실패", "필터 생성에 실패하였습니다.")

    def handle_delete_filter(self):
        if not self.listbox_filters.curselection():
            messagebox.showwarning("선택 오류", "삭제할 필터를 선택해주세요.")
            return
        index = self.listbox_filters.curselection()[0]
        filter_name = self.listbox_filters.get(index)
        confirm = messagebox.askyesno("필터 삭제", f"'{filter_name}' 필터를 삭제하시겠습니까?")
        if confirm:
            success = delete_filter(self.user_id, filter_name)
            if success:
                messagebox.showinfo("필터 삭제", "필터가 성공적으로 삭제되었습니다.")
                self.refresh_filter_list()
            else:
                messagebox.showerror("필터 삭제 실패", "필터 삭제에 실패하였습니다.")
