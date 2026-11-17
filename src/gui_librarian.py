import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import models

class LibrarianDashboard(tk.Frame):
    def __init__(self, parent, controller, role=""):
        super().__init__(parent)
        self.controller = controller
        self.role = role
        self.configure(bg="#f4f6f9")

        header_frame = tk.Frame(self, bg="#2c3e50", height=50)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="HỆ THỐNG QUẢN LÝ THƯ VIỆN - PHÂN HỆ THỦ THƯ", 
                 font=("Arial", 14, "bold"), bg="#2c3e50", fg="white").pack(side="left", padx=20, pady=12)
        
        tk.Button(header_frame, text="Đăng Xuất", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), 
                  width=10, command=self.logout).pack(side="right", padx=20, pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)

        self.tab_books = tk.Frame(self.notebook, bg="#f4f6f9")
        self.tab_borrow = tk.Frame(self.notebook, bg="#f4f6f9")
        self.tab_overdue = tk.Frame(self.notebook, bg="#f4f6f9")

        self.notebook.add(self.tab_books, text="  1. Quản Lý Sách & Bản Sao  ")
        self.notebook.add(self.tab_borrow, text="  2. Lập Phiếu Mượn & Trả Sách  ")
        self.notebook.add(self.tab_overdue, text="  3. Thống Kê Quá Hạn  ")

        self.setup_books_tab()
        self.setup_borrow_tab()
        self.setup_overdue_tab()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        selected_tab = self.notebook.index(self.notebook.select())
        if selected_tab == 0:
            self.load_books_data()
        elif selected_tab == 1:
            self.refresh_borrow_combos()
            self.load_borrow_records()
        elif selected_tab == 2:
            self.load_overdue_records()

    def setup_books_tab(self):
        self.categories = models.get_categories()
        self.cat_map = {name: cid for cid, name in self.categories}
        self.selected_book_id = None

        frame_form = tk.Frame(self.tab_books, bg="#f4f6f9")
        frame_form.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_form, text="ISBN:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_isbn = tk.Entry(frame_form, width=18, font=("Arial", 10))
        self.ent_isbn.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Tên sách:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.ent_title = tk.Entry(frame_form, width=32, font=("Arial", 10))
        self.ent_title.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_form, text="Tác giả:", bg="#f4f6f9", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_author = tk.Entry(frame_form, width=18, font=("Arial", 10))
        self.ent_author.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Thể loại:", bg="#f4f6f9", font=("Arial", 10)).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.cb_category = ttk.Combobox(frame_form, values=list(self.cat_map.keys()), width=29, state="readonly", font=("Arial", 10))
        if self.categories:
            self.cb_category.current(0)
        self.cb_category.grid(row=1, column=3, padx=5, pady=5)

        frame_btn = tk.Frame(self.tab_books, bg="#f4f6f9")
        frame_btn.pack(fill="x", padx=15, pady=5)

        tk.Button(frame_btn, text="+ Thêm Sách", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=12, command=self.add_book).pack(side="left", padx=4)
        tk.Button(frame_btn, text="Cập Nhật", bg="#f39c12", fg="white", font=("Arial", 10, "bold"), width=10, command=self.edit_book).pack(side="left", padx=4)
        tk.Button(frame_btn, text="Ẩn / Hiện", bg="#7f8c8d", fg="white", font=("Arial", 10, "bold"), width=10, command=self.toggle_hidden).pack(side="left", padx=4)
        tk.Button(frame_btn, text="+ Thêm Bản Sao", bg="#2980b9", fg="white", font=("Arial", 10, "bold"), width=14, command=self.add_copies).pack(side="left", padx=4)
        tk.Button(frame_btn, text="Làm Mới Form", bg="#95a5a6", fg="white", font=("Arial", 10, "bold"), width=12, command=self.clear_book_form).pack(side="left", padx=4)

        columns = ("ID", "ISBN", "Tên sách", "Tác giả", "Thể loại", "Khả dụng / Tổng", "Trạng thái")
        self.tree_books = ttk.Treeview(self.tab_books, columns=columns, show="headings", height=14)
        widths = [45, 95, 220, 140, 130, 110, 85]
        for col, w in zip(columns, widths):
            self.tree_books.heading(col, text=col)
            anchor = "center" if col in ("ID", "ISBN", "Khả dụng / Tổng", "Trạng thái") else "w"
            self.tree_books.column(col, width=w, anchor=anchor)

        self.tree_books.pack(fill="both", expand=True, padx=15, pady=10)
        self.tree_books.bind("<ButtonRelease-1>", self.on_book_select)
        self.load_books_data()

    def load_books_data(self):
        for item in self.tree_books.get_children():
            self.tree_books.delete(item)
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        try:
            query = """
                SELECT b.id, b.isbn, b.title, b.author, c.name, b.is_hidden,
                       (SELECT COUNT(*) FROM book_copies WHERE book_id = b.id AND status = 'available'),
                       (SELECT COUNT(*) FROM book_copies WHERE book_id = b.id)
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                cat_name = row[4] if row[4] else "Chưa phân loại"
                copy_info = f"{row[6]} / {row[7]}"
                status_text = "Đã ẩn" if row[5] == 1 else "Hiển thị"
                self.tree_books.insert("", "end", values=(row[0], row[1], row[2], row[3], cat_name, copy_info, status_text))
        finally:
            conn.close()

    def on_book_select(self, event):
        selected = self.tree_books.focus()
        if not selected:
            return
        values = self.tree_books.item(selected, 'values')
        self.clear_book_form()
        self.selected_book_id = values[0]
        self.ent_isbn.insert(0, values[1])
        self.ent_title.insert(0, values[2])
        self.ent_author.insert(0, values[3])
        if values[4] in self.cat_map:
            self.cb_category.set(values[4])

    def add_book(self):
        isbn = self.ent_isbn.get().strip()
        title = self.ent_title.get().strip()
        author = self.ent_author.get().strip()
        cat_id = self.cat_map.get(self.cb_category.get())
        if not isbn or not title or not author:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ ISBN, Tên sách và Tác giả!")
            return
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO books (isbn, title, author, category_id) VALUES (?, ?, ?, ?)", (isbn, title, author, cat_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Đã thêm đầu sách mới!")
            self.clear_book_form()
            self.load_books_data()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã ISBN này đã tồn tại!")
        finally:
            conn.close()

    def edit_book(self):
        if not self.selected_book_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một sách trên bảng!")
            return
        isbn = self.ent_isbn.get().strip()
        title = self.ent_title.get().strip()
        author = self.ent_author.get().strip()
        cat_id = self.cat_map.get(self.cb_category.get())
        if not isbn or not title or not author:
            messagebox.showwarning("Cảnh báo", "Không được để trống thông tin!")
            return
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE books SET isbn=?, title=?, author=?, category_id=? WHERE id=?", (isbn, title, author, cat_id, self.selected_book_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Đã cập nhật đầu sách!")
            self.load_books_data()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã ISBN bị trùng lặp!")
        finally:
            conn.close()

    def toggle_hidden(self):
        if not self.selected_book_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một sách trên bảng!")
            return
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE books SET is_hidden = 1 - is_hidden WHERE id=?", (self.selected_book_id,))
            conn.commit()
            self.load_books_data()
        finally:
            conn.close()

    def add_copies(self):
        if not self.selected_book_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đầu sách cần thêm bản sao!")
            return
        qty = simpledialog.askinteger("Thêm bản sao", "Nhập số lượng bản sao muốn nhập kho:", minvalue=1, maxvalue=100)
        if qty:
            conn = sqlite3.connect(models.DB_PATH)
            cursor = conn.cursor()
            try:
                for _ in range(qty):
                    cursor.execute("INSERT INTO book_copies (book_id, status) VALUES (?, 'available')", (self.selected_book_id,))
                conn.commit()
                messagebox.showinfo("Thành công", f"Đã thêm {qty} bản sao khả dụng!")
                self.load_books_data()
            finally:
                conn.close()

    def clear_book_form(self):
        self.selected_book_id = None
        self.ent_isbn.delete(0, 'end')
        self.ent_title.delete(0, 'end')
        self.ent_author.delete(0, 'end')

    def setup_borrow_tab(self):
        form_frame = tk.LabelFrame(self.tab_borrow, text=" Lập Phiếu Mượn Mới (FR05) ", font=("Arial", 10, "bold"), bg="#f4f6f9", fg="#2c3e50")
        form_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(form_frame, text="Độc giả:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=0, padx=8, pady=10, sticky="e")
        self.cb_readers = ttk.Combobox(form_frame, width=22, state="readonly", font=("Arial", 10))
        self.cb_readers.grid(row=0, column=1, padx=5, pady=10)

        tk.Label(form_frame, text="Đầu sách:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=2, padx=8, pady=10, sticky="e")
        self.cb_borrow_books = ttk.Combobox(form_frame, width=32, state="readonly", font=("Arial", 10))
        self.cb_borrow_books.grid(row=0, column=3, padx=5, pady=10)

        tk.Label(form_frame, text="Số ngày mượn:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=4, padx=8, pady=10, sticky="e")
        self.ent_days = tk.Entry(form_frame, width=6, font=("Arial", 10))
        self.ent_days.insert(0, "7")
        self.ent_days.grid(row=0, column=5, padx=5, pady=10)

        tk.Button(form_frame, text="Xác Nhận Mượn", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=14,
                  command=self.create_borrow_record).grid(row=0, column=6, padx=12, pady=10)

        action_frame = tk.Frame(self.tab_borrow, bg="#f4f6f9")
        action_frame.pack(fill="x", padx=15, pady=5)
        
        tk.Label(action_frame, text="Danh sách phiếu đang mượn & lịch sử:", font=("Arial", 10, "bold"), bg="#f4f6f9", fg="#34495e").pack(side="left")
        tk.Button(action_frame, text="Ghi Nhận Trả Sách (FR06)", bg="#2980b9", fg="white", font=("Arial", 10, "bold"), width=22,
                  command=self.return_book).pack(side="right", padx=5)

        columns = ("Mã Phiếu", "Mã Bản Sao", "Độc Giả", "Tên Sách", "Ngày Mượn", "Hạn Trả", "Ngày Trả", "Trạng Thái")
        self.tree_borrow = ttk.Treeview(self.tab_borrow, columns=columns, show="headings", height=14)
        widths = [65, 80, 100, 220, 95, 95, 95, 100]
        for col, w in zip(columns, widths):
            self.tree_borrow.heading(col, text=col)
            anchor = "center" if col not in ("Độc Giả", "Tên Sách") else "w"
            self.tree_borrow.column(col, width=w, anchor=anchor)

        self.tree_borrow.pack(fill="both", expand=True, padx=15, pady=10)

        self.reader_map = {}
        self.book_borrow_map = {}
        self.refresh_borrow_combos()
        self.load_borrow_records()

    def refresh_borrow_combos(self):
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, username FROM users WHERE role='reader'")
            readers = cursor.fetchall()
            self.reader_map = {f"{r[1]} (ID: {r[0]})": r[0] for r in readers}
            self.cb_readers['values'] = list(self.reader_map.keys())
            if readers:
                self.cb_readers.current(0)

            cursor.execute("""
                SELECT b.id, b.title, 
                       (SELECT COUNT(*) FROM book_copies WHERE book_id = b.id AND status = 'available')
                FROM books b WHERE b.is_hidden = 0
            """)
            books = cursor.fetchall()
            self.book_borrow_map = {f"{b[1]} [Còn: {b[2]}]": b[0] for b in books}
            self.cb_borrow_books['values'] = list(self.book_borrow_map.keys())
            if books:
                self.cb_borrow_books.current(0)
        finally:
            conn.close()

    def create_borrow_record(self):
        reader_key = self.cb_readers.get()
        book_key = self.cb_borrow_books.get()
        days_str = self.ent_days.get().strip()

        if not reader_key or not book_key:
            messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu độc giả hoặc đầu sách!")
            return
        if not days_str.isdigit() or int(days_str) <= 0:
            messagebox.showwarning("Cảnh báo", "Số ngày mượn phải là số nguyên dương!")
            return

        reader_id = self.reader_map[reader_key]
        book_id = self.book_borrow_map[book_key]
        days = int(days_str)

        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM book_copies WHERE book_id=? AND status='available' LIMIT 1", (book_id,))
            copy_row = cursor.fetchone()

            if not copy_row:
                messagebox.showerror("Hết sách (FR05)", "Đầu sách này hiện không còn bản sao khả dụng trong kho!")
                return

            copy_id = copy_row[0]
            borrow_date = datetime.now().strftime("%Y-%m-%d")
            due_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO borrow_records (copy_id, reader_id, borrow_date, due_date, return_date)
                VALUES (?, ?, ?, ?, NULL)
            """, (copy_id, reader_id, borrow_date, due_date))

            cursor.execute("UPDATE book_copies SET status='borrowed' WHERE id=?", (copy_id,))
            conn.commit()

            messagebox.showinfo("Thành công", f"Đã lập phiếu mượn thành công!\nMã bản sao: #{copy_id}\nHạn trả: {due_date}")
            self.refresh_borrow_combos()
            self.load_borrow_records()
        finally:
            conn.close()

    def load_borrow_records(self):
        for item in self.tree_borrow.get_children():
            self.tree_borrow.delete(item)

        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        try:
            query = """
                SELECT br.id, br.copy_id, u.username, b.title, br.borrow_date, br.due_date, br.return_date
                FROM borrow_records br
                JOIN users u ON br.reader_id = u.id
                JOIN book_copies bc ON br.copy_id = bc.id
                JOIN books b ON bc.book_id = b.id
                ORDER BY br.return_date IS NOT NULL, br.id DESC
            """
            cursor.execute(query)
            today_str = datetime.now().strftime("%Y-%m-%d")

            for row in cursor.fetchall():
                ret_date = row[6] if row[6] else "Chưa trả"
                if row[6]:
                    status = "Đã trả"
                elif row[5] < today_str:
                    status = "QUÁ HẠN"
                else:
                    status = "Đang mượn"
                self.tree_borrow.insert("", "end", values=(row[0], f"#{row[1]}", row[2], row[3], row[4], row[5], ret_date, status))
        finally:
            conn.close()

    def return_book(self):
        selected = self.tree_borrow.focus()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một phiếu mượn trên bảng để trả sách!")
            return

        values = self.tree_borrow.item(selected, 'values')
        record_id = values[0]
        copy_id = values[1].replace("#", "")
        status = values[7]

        if status == "Đã trả":
            messagebox.showinfo("Thông báo", "Phiếu mượn này đã được trả trước đó!")
            return

        if messagebox.askyesno("Xác nhận trả sách", f"Xác nhận độc giả trả bản sao #{copy_id} (Phiếu #{record_id})?"):
            conn = sqlite3.connect(models.DB_PATH)
            cursor = conn.cursor()
            try:
                return_date = datetime.now().strftime("%Y-%m-%d")
                cursor.execute("UPDATE borrow_records SET return_date=? WHERE id=?", (return_date, record_id))
                cursor.execute("UPDATE book_copies SET status='available' WHERE id=?", (copy_id,))
                conn.commit()
                messagebox.showinfo("Thành công", "Đã ghi nhận trả sách và cập nhật kho khả dụng!")
                self.refresh_borrow_combos()
                self.load_borrow_records()
            finally:
                conn.close()

    def setup_overdue_tab(self):
        top_frame = tk.Frame(self.tab_overdue, bg="#f4f6f9")
        top_frame.pack(fill="x", padx=15, pady=12)

        tk.Label(top_frame, text="DANH SÁCH CÁC PHIẾU MƯỢN QUÁ HẠN CHƯA TRẢ (FR06)", 
                 font=("Arial", 11, "bold"), bg="#f4f6f9", fg="#c0392b").pack(side="left")

        tk.Button(top_frame, text="Làm Mới Danh Sách", bg="#34495e", fg="white", font=("Arial", 10, "bold"),
                  command=self.load_overdue_records).pack(side="right")

        columns = ("Mã Phiếu", "Độc Giả", "Mã Bản Sao", "Tên Sách", "Ngày Mượn", "Hạn Trả", "Số Ngày Trễ")
        self.tree_overdue = ttk.Treeview(self.tab_overdue, columns=columns, show="headings", height=16)
        widths = [70, 120, 85, 250, 100, 100, 100]
        for col, w in zip(columns, widths):
            self.tree_overdue.heading(col, text=col)
            anchor = "center" if col not in ("Độc Giả", "Tên Sách") else "w"
            self.tree_overdue.column(col, width=w, anchor=anchor)

        self.tree_overdue.pack(fill="both", expand=True, padx=15, pady=10)
        self.load_overdue_records()

    def load_overdue_records(self):
        for item in self.tree_overdue.get_children():
            self.tree_overdue.delete(item)

        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        try:
            today = datetime.now()
            today_str = today.strftime("%Y-%m-%d")

            query = """
                SELECT br.id, u.username, br.copy_id, b.title, br.borrow_date, br.due_date
                FROM borrow_records br
                JOIN users u ON br.reader_id = u.id
                JOIN book_copies bc ON br.copy_id = bc.id
                JOIN books b ON bc.book_id = b.id
                WHERE br.return_date IS NULL AND br.due_date < ?
                ORDER BY br.due_date ASC
            """
            cursor.execute(query, (today_str,))
            for row in cursor.fetchall():
                due_dt = datetime.strptime(row[5], "%Y-%m-%d")
                overdue_days = (today - due_dt).days
                self.tree_overdue.insert("", "end", values=(row[0], row[1], f"#{row[2]}", row[3], row[4], row[5], f"{overdue_days} ngày"))
        finally:
            conn.close()

    def logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất không?"):
            self.destroy()
            self.controller.show_login_screen()