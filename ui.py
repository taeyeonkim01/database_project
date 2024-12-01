import tkinter as tk
from tkinter import ttk, messagebox
from login import login
from search import search_products
from filters import get_user_filters, create_filter, delete_filter
from database import connect_to_db  # connect_to_db 함수 임포트

class CosmeticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cosmetic Product Search")
        self.root.geometry("1000x600")  # 창 크기 조정

        self.is_logged_in = tk.BooleanVar(value=False)
        self.user_name = None
        self.user_id = None
        self.search_mode = tk.StringVar(value="default")
        self.exclude_ingredient = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 좌측 프레임 (로그인 영역과 필터 목록)
        left_frame = tk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 우측 프레임 (검색 영역과 결과 테이블)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_login_area(left_frame)
        self.create_filter_list(left_frame)
        self.create_search_area(right_frame)
        self.create_mode_buttons(right_frame)
        self.create_results_table(right_frame)

    def create_login_area(self, parent):
        login_frame = tk.LabelFrame(parent, text="로그인", padx=10, pady=10)
        login_frame.pack(fill=tk.X, padx=10, pady=10)

        self.label_welcome = tk.Label(login_frame, text="로그인해주세요.", font=("Arial", 12))
        self.label_welcome.pack(pady=5)

        self.entry_email = tk.Entry(login_frame, width=25)
        self.entry_email.pack(pady=5)
        self.add_placeholder(self.entry_email, "이메일")

        self.entry_password = tk.Entry(login_frame, width=25)
        self.entry_password.pack(pady=5)
        self.add_placeholder(self.entry_password, "비밀번호", show='*')

        self.button_login = tk.Button(login_frame, text="로그인", command=self.handle_login)
        self.button_login.pack(pady=5)

    def add_placeholder(self, entry, placeholder, show=None):
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg='black', show=show)

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg='grey', show='')

        entry.insert(0, placeholder)
        entry.config(fg='grey')
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    def create_filter_list(self, parent):
        self.filter_frame = tk.LabelFrame(parent, text="사용자 필터 목록", padx=10, pady=10)
        self.filter_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.listbox_filters = tk.Listbox(self.filter_frame, width=30, height=15)
        self.listbox_filters.pack(pady=5, fill=tk.BOTH, expand=True)

        self.listbox_filters.bind('<Double-Button-1>', self.handle_filter_double_click)

        button_frame = tk.Frame(self.filter_frame)
        button_frame.pack(pady=5)

        self.button_create_filter = tk.Button(button_frame, text="필터 생성", command=self.open_create_filter_window)
        self.button_create_filter.grid(row=0, column=0, padx=5)

        self.button_delete_filter = tk.Button(button_frame, text="필터 삭제", command=self.handle_delete_filter)
        self.button_delete_filter.grid(row=0, column=1, padx=5)

        self.toggle_filter_widgets(state='disabled')

    def toggle_filter_widgets(self, state='normal'):
        """
        사용자 필터 관련 위젯 활성화/비활성화
        """
        widgets = [self.listbox_filters, self.button_create_filter, self.button_delete_filter]
        for widget in widgets:
            widget.config(state=state)

    def create_search_area(self, parent):
        search_frame = tk.Frame(parent)
        search_frame.pack(pady=10, padx=10, fill=tk.X)

        self.entry_search = tk.Entry(search_frame, width=50, font=("Arial", 14))
        self.entry_search.grid(row=0, column=0, padx=5)

        self.checkbox_exclude = tk.Checkbutton(search_frame, text="성분 제외", variable=self.exclude_ingredient)
        self.checkbox_exclude.grid(row=0, column=1, padx=5)

        btn_search = tk.Button(search_frame, text="검색", command=self.handle_search, font=("Arial", 12))
        btn_search.grid(row=0, column=2, padx=5)

        self.label_mode = tk.Label(parent, text="모드: 기본 (브랜드/제품 검색)", font=("Arial", 12))
        self.label_mode.pack(pady=5)

    def create_mode_buttons(self, parent):
        mode_frame = tk.Frame(parent)
        mode_frame.pack(pady=5)

        btn_default = tk.Button(mode_frame, text="기본 검색", command=lambda: self.set_search_mode("default"))
        btn_default.grid(row=0, column=0, padx=5)

        btn_category = tk.Button(mode_frame, text="카테고리 검색", command=lambda: self.set_search_mode("category"))
        btn_category.grid(row=0, column=1, padx=5)

        btn_ingredient = tk.Button(mode_frame, text="성분 검색", command=lambda: self.set_search_mode("ingredient"))
        btn_ingredient.grid(row=0, column=2, padx=5)

    def create_results_table(self, parent):
        columns = ("product_name", "brand_name", "category_name", "price")
        self.treeview_results = ttk.Treeview(parent, columns=columns, show="headings", height=20)
        self.treeview_results.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        for col in columns:
            self.treeview_results.heading(col, text=col.replace("_", " ").capitalize())
            self.treeview_results.column(col, width=100, anchor='center')

        self.treeview_results.bind("<Double-1>", self.handle_result_double_click)

    def handle_result_double_click(self, event):
        """
        검색 결과 테이블에서 제품 행을 더블클릭하면 해당 제품의 성분 정보를 표시.
        """
        selected_item = self.treeview_results.selection()
        if not selected_item:
            return

        product_name = self.treeview_results.item(selected_item, "values")[0]

        try:
            conn = connect_to_db()
            if conn is None:
                raise Exception("데이터베이스 연결 실패")

            with conn.cursor() as cursor:
                query = """
                SELECT i.name AS ingredient_name, i.description
                FROM Products p
                JOIN Product_Ingredients pi ON p.product_id = pi.product_id
                JOIN Ingredients i ON pi.ingredient_id = i.ingredient_id
                WHERE p.name = %s
                """
                cursor.execute(query, (product_name,))
                results = cursor.fetchall()

            if not results:
                messagebox.showinfo("성분 정보", f"'{product_name}' 제품에 대한 성분 정보가 없습니다.")
                return

            ingredients_window = tk.Toplevel(self.root)
            ingredients_window.title(f"{product_name}의 성분 정보")
            ingredients_window.geometry("800x600")

            tk.Label(ingredients_window, text=f"{product_name}의 성분 정보", font=("Arial", 14, "bold")).pack(pady=10)

            treeview_ingredients = ttk.Treeview(ingredients_window, columns=("ingredient_name", "description"), show="headings", height=15)
            treeview_ingredients.pack(pady=10, fill=tk.BOTH, expand=True)

            treeview_ingredients.heading("ingredient_name", text="성분 이름")
            treeview_ingredients.heading("description", text="성분 설명")

            for ingredient in results:
                treeview_ingredients.insert("", "end", values=ingredient)

            tk.Button(ingredients_window, text="닫기", command=ingredients_window.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("오류", f"성분 정보를 가져오는 중 오류가 발생했습니다: {e}")
        finally:
            if conn:
                conn.close()

    def handle_search(self):
        if not self.is_logged_in.get():
            messagebox.showwarning("로그인 필요", "검색 기능을 이용하려면 로그인이 필요합니다.")
            return

        search_term = self.entry_search.get().strip()
        if not search_term:
            messagebox.showwarning("입력 오류", "검색어를 입력해주세요.")
            return

        results = search_products(
            search_term,
            self.search_mode.get(),
            self.exclude_ingredient.get(),
            user_id=self.user_id,
            filter_name=None
        )
        self.display_results(results)

    def handle_filter_double_click(self, event):
        if not self.is_logged_in.get():
            messagebox.showwarning("로그인 필요", "필터를 사용하려면 로그인이 필요합니다.")
            return

        if not self.listbox_filters.curselection():
            return
        index = self.listbox_filters.curselection()[0]
        filter_name = self.listbox_filters.get(index)

        # 검색어 없이 필터만 사용하여 검색 수행
        results = search_products(
            search_term=None,
            search_mode="filter_only",
            is_exclude=False,
            user_id=self.user_id,
            filter_name=filter_name
        )
        self.display_results(results)


        # 필터 선택 해제하여 이후 검색에 영향을 주지 않도록
  
        self.listbox_filters.selection_clear(0, tk.END)

    def display_results(self, results):
        self.treeview_results.delete(*self.treeview_results.get_children())
        for row in results:
            self.treeview_results.insert("", "end", values=row)

    def handle_login(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        if not email or not password or email == "이메일" or password == "비밀번호":
            messagebox.showwarning("입력 오류", "이메일과 비밀번호를 모두 입력해주세요.")
            return

        success, user_info = login(email, password)
        if success:
            self.is_logged_in.set(True)
            self.user_name = user_info['name']
            self.user_id = user_info['user_id']
            self.label_welcome.config(text=f"환영합니다, {self.user_name}님!")
            self.entry_email.pack_forget()
            self.entry_password.pack_forget()
            self.button_login.pack_forget()
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
        create_filter_window.geometry("500x600")

        tk.Label(create_filter_window, text="필터 이름:").pack(pady=5)
        entry_filter_name = tk.Entry(create_filter_window, width=30)
        entry_filter_name.pack(pady=5)

        # 스크롤 가능한 캔버스 생성
        canvas = tk.Canvas(create_filter_window)
        scrollbar = tk.Scrollbar(create_filter_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 성분 목록 가져오기
        ingredients = self.get_all_ingredients()

        # 성분별로 체크박스 생성
        self.include_vars = {}
        self.exclude_vars = {}

        for ing_id, ing_name in ingredients:
            frame = tk.Frame(scrollable_frame)
            frame.pack(fill="x", padx=5, pady=2)

            label = tk.Label(frame, text=ing_name, width=30, anchor='w')
            label.pack(side="left")

            include_var = tk.BooleanVar()
            exclude_var = tk.BooleanVar()

            self.include_vars[ing_id] = include_var
            self.exclude_vars[ing_id] = exclude_var

            include_cb = tk.Checkbutton(frame, text="포함", variable=include_var,
                                        command=lambda iv=include_var, ev=exclude_var: self.sync_checkboxes(iv, ev))
            include_cb.pack(side="left")

            exclude_cb = tk.Checkbutton(frame, text="제외", variable=exclude_var,
                                        command=lambda iv=include_var, ev=exclude_var: self.sync_checkboxes(ev, iv))
            exclude_cb.pack(side="left")

        tk.Button(
            create_filter_window,
            text="생성",
            command=lambda: self.handle_create_filter(
                entry_filter_name.get(),
                create_filter_window
            )
        ).pack(pady=10)

    def sync_checkboxes(self, var1, var2):
        """
        하나의 체크박스를 선택하면 다른 하나를 해제하여 포함과 제외가 동시에 선택되지 않도록 합니다.
        """
        if var1.get():
            var2.set(False)

    def handle_create_filter(self, filter_name, window):
        if not filter_name:
            messagebox.showwarning("입력 오류", "필터 이름을 입력해주세요.")
            return

        include_ingredients = [ing_id for ing_id, var in self.include_vars.items() if var.get()]
        exclude_ingredients = [ing_id for ing_id, var in self.exclude_vars.items() if var.get()]

        # 포함 및 제외 성분 중복 확인 (이미 sync_checkboxes로 처리되지만 추가 확인)
        overlap = set(include_ingredients) & set(exclude_ingredients)
        if overlap:
            messagebox.showerror("입력 오류", "같은 성분을 포함과 제외에 동시에 선택할 수 없습니다.")
            return

        success = create_filter(self.user_id, filter_name, include_ingredients, exclude_ingredients)
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


    def get_all_ingredients(self):
        """
        데이터베이스에서 모든 성분의 ID와 이름을 가져옵니다.
        """
        conn = connect_to_db()
        if conn is None:
            return []

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT ingredient_id, name FROM Ingredients")
                ingredients = cursor.fetchall()
                return ingredients
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching ingredients: {e}")
            return []
        finally:
            conn.close()
            
    def set_search_mode(self, mode):
        self.search_mode.set(mode)
        self.label_mode.config(text=f"모드: {mode.capitalize()} 검색")
        if mode == "ingredient":
            self.checkbox_exclude.grid()
        else:
            self.checkbox_exclude.grid_remove()

