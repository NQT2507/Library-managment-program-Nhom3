import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import models

class ReaderDashboard(tk.Frame):
    def __init__(self, parent, controller, role=""):
        super().__init__(parent)
        self.controller = controller
        self.role = role
        self.configure(bg="#f4f6f9")

        self.categories = models.get_categories()
        self.cat_options = ["Tất cả thể loại"] + [name for _, name in self.categories]

        # Tiêu đề
        lbl_title = tk.Label(self, text="TRA CỨU DANH MỤC SÁCH (ĐỘC GIẢ)", 
                             font=("Arial", 16, "bold"), bg="#f4f6f9", fg="#2c3e50")
        lbl_title.pack(pady=15)

        # --- Thanh Tìm kiếm & Lọc (FR04) ---
        search_frame = tk.Frame(self, bg="#f4f6f9")
        search_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(search_frame, text="Từ khóa:", bg="#f4f6f9", font=("Arial", 10)).pack(side="left", padx=5)
        self.ent_keyword = tk.Entry(search_frame, width=30, font=("Arial", 10))
        self.ent_keyword.pack(side="left", padx=5)

        tk.Label(search_frame, text="Thể loại:", bg="#f4f6f9", font=("Arial", 10)).pack(side="left", padx=5)
        self.cb_filter_cat = ttk.Combobox(search_frame, values=self.cat_options, width=22, state="readonly", font=("Arial", 10))
        self.cb_filter_cat.current(0)
        self.cb_filter_cat.pack(side="left", padx=5)

        tk.Button(search_frame, text="Tìm Kiếm", bg="#2980b9", fg="white", font=("Arial", 10, "bold"), width=12, 
                  command=self.search_books).pack(side="left", padx=10)
        
        tk.Button(search_frame, text="Đăng Xuất", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=10, 
                  command=self.logout).pack(side="right", padx=5)

        # --- Bảng Kết quả ---
        columns = ("ID", "ISBN", "Tên sách", "Tác giả", "Thể loại", "Số bản còn sẵn")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)

        widths = [50, 100, 260, 160, 140, 110]
        for col, w in zip(columns, widths):
            self.tree.heading(col, text=col)
            anchor = "center" if col in ("ID", "ISBN", "Số bản còn sẵn") else "w"
            self.tree.column(col, width=w, anchor=anchor)

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        self.search_books()

    def search_books(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        keyword = f"%{self.ent_keyword.get().strip()}%"
        selected_cat = self.cb_filter_cat.get()

        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        try:
            # Chỉ hiển thị sách có is_hidden = 0 (FR02)
            query = """
                SELECT b.id, b.isbn, b.title, b.author, c.name,
                       (SELECT COUNT(*) FROM book_copies WHERE book_id = b.id AND status = 'available')
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                WHERE b.is_hidden = 0 AND (b.title LIKE ? OR b.author LIKE ?)
            """
            params = [keyword, keyword]

            if selected_cat != "Tất cả thể loại":
                query += " AND c.name = ?"
                params.append(selected_cat)

            cursor.execute(query, params)
            for row in cursor.fetchall():
                cat_name = row[4] if row[4] else "Chưa phân loại"
                avail_text = f"{row[5]} cuốn" if row[5] > 0 else "Hết sách"
                self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], cat_name, avail_text))
        finally:
            conn.close()

    def logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất không?"):
            self.destroy()
            self.controller.show_login_screen()