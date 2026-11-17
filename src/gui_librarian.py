import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import models

class LibrarianDashboard(tk.Frame):
    def __init__(self, parent, controller, role=""):
        super().__init__(parent)
        self.controller = controller
        self.role = role
        self.configure(bg="#f4f6f9")
        
        # Lấy danh sách thể loại từ DB
        self.categories = models.get_categories()
        self.cat_map = {name: cid for cid, name in self.categories}
        self.cat_rev_map = {cid: name for cid, name in self.categories}

        # Tiêu đề
        lbl_title = tk.Label(self, text="QUẢN LÝ ĐẦU SÁCH & BẢN SAO (THỦ THƯ)", 
                             font=("Arial", 16, "bold"), bg="#f4f6f9", fg="#2c3e50")
        lbl_title.pack(pady=10)

        # --- Khu vực Nhập liệu (Form) ---
        frame_form = tk.Frame(self, bg="#f4f6f9")
        frame_form.pack(fill="x", padx=20, pady=5)

        # Hàng 1: ISBN & Tên sách
        tk.Label(frame_form, text="ISBN:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_isbn = tk.Entry(frame_form, width=18, font=("Arial", 10))
        self.ent_isbn.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Tên sách:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.ent_title = tk.Entry(frame_form, width=32, font=("Arial", 10))
        self.ent_title.grid(row=0, column=3, padx=5, pady=5)

        # Hàng 2: Tác giả & Thể loại
        tk.Label(frame_form, text="Tác giả:", bg="#f4f6f9", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_author = tk.Entry(frame_form, width=18, font=("Arial", 10))
        self.ent_author.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Thể loại:", bg="#f4f6f9", font=("Arial", 10)).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.cb_category = ttk.Combobox(frame_form, values=list(self.cat_map.keys()), width=29, state="readonly", font=("Arial", 10))
        if self.categories:
            self.cb_category.current(0)
        self.cb_category.grid(row=1, column=3, padx=5, pady=5)

        self.selected_book_id = None

        # --- Khu vực Nút bấm ---
        frame_btn = tk.Frame(self, bg="#f4f6f9")
        frame_btn.pack(fill="x", padx=20, pady=8)

        tk.Button(frame_btn, text="+ Thêm Sách", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=11, command=self.add_book).pack(side="left", padx=4)
        tk.Button(frame_btn, text="Cập Nhật", bg="#f39c12", fg="white", font=("Arial", 10, "bold"), width=10, command=self.edit_book).pack(side="left", padx=4)
        tk.Button(frame_btn, text="Ẩn / Hiện", bg="#7f8c8d", fg="white", font=("Arial", 10, "bold"), width=10, command=self.toggle_hidden).pack(side="left", padx=4)
        tk.Button(frame_btn, text="+ Thêm Bản Sao", bg="#2980b9", fg="white", font=("Arial", 10, "bold"), width=14, command=self.add_copies).pack(side="left", padx=4)
        tk.Button(frame_btn, text="Làm Mới", bg="#95a5a6", fg="white", font=("Arial", 10, "bold"), width=9, command=self.clear_form).pack(side="left", padx=4)
        
        tk.Button(frame_btn, text="Đăng Xuất", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=10, command=self.logout).pack(side="right", padx=4)

        # --- Khu vực Bảng Dữ liệu (Treeview) ---
        columns = ("ID", "ISBN", "Tên sách", "Tác giả", "Thể loại", "Khả dụng / Tổng", "Trạng thái")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        widths = [45, 95, 220, 140, 130, 110, 85]
        for col, w in zip(columns, widths):
            self.tree.heading(col, text=col)
            anchor = "center" if col in ("ID", "ISBN", "Khả dụng / Tổng", "Trạng thái") else "w"
            self.tree.column(col, width=w, anchor=anchor)
        
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        try:
            # Truy vấn kết hợp đếm số bản sao khả dụng và tổng số bản sao (FR03)
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
                self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], cat_name, copy_info, status_text))
        finally:
            conn.close()

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, 'values')
        self.clear_form()
        
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
            cursor.execute("INSERT INTO books (isbn, title, author, category_id) VALUES (?, ?, ?, ?)", 
                           (isbn, title, author, cat_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Đã thêm đầu sách mới! Hãy bấm '+ Thêm Bản Sao' để nhập số lượng.")
            self.clear_form()
            self.load_data()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã ISBN này đã tồn tại!")
        finally:
            conn.close()

    def edit_book(self):
        if not self.selected_book_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một sách từ bảng để sửa!")
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
            cursor.execute("UPDATE books SET isbn=?, title=?, author=?, category_id=? WHERE id=?", 
                           (isbn, title, author, cat_id, self.selected_book_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Đã cập nhật đầu sách!")
            self.load_data()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã ISBN bị trùng với sách khác!")
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
            self.load_data()
        finally:
            conn.close()

    def add_copies(self):
        if not self.selected_book_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một đầu sách trên bảng để thêm bản sao!")
            return
        qty = simpledialog.askinteger("Thêm bản sao vật lý", "Nhập số lượng bản sao muốn thêm vào kho:", minvalue=1, maxvalue=100)
        if qty:
            conn = sqlite3.connect(models.DB_PATH)
            cursor = conn.cursor()
            try:
                for _ in range(qty):
                    cursor.execute("INSERT INTO book_copies (book_id, status) VALUES (?, 'available')", (self.selected_book_id,))
                conn.commit()
                messagebox.showinfo("Thành công", f"Đã thêm {qty} bản sao khả dụng vào kho!")
                self.load_data()
            finally:
                conn.close()

    def clear_form(self):
        self.selected_book_id = None
        self.ent_isbn.delete(0, 'end')
        self.ent_title.delete(0, 'end')
        self.ent_author.delete(0, 'end')

    def logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất không?"):
            self.destroy()
            self.controller.show_login_screen()