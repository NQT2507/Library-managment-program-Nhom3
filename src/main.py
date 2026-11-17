import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import models

class LibrarianDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f4f6f9")
        
        # Tiêu đề
        lbl_title = tk.Label(self, text="QUẢN LÝ ĐẦU SÁCH", font=("Arial", 18, "bold"), bg="#f4f6f9", fg="#2c3e50")
        lbl_title.pack(pady=15)

        # --- Khu vực Nhập liệu (Form) ---
        frame_form = tk.Frame(self, bg="#f4f6f9")
        frame_form.pack(fill="x", padx=20, pady=10)

        # Hàng 1
        tk.Label(frame_form, text="Tên sách:", bg="#f4f6f9").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_title = tk.Entry(frame_form, width=30)
        self.ent_title.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Tác giả:", bg="#f4f6f9").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.ent_author = tk.Entry(frame_form, width=25)
        self.ent_author.grid(row=0, column=3, padx=5, pady=5)

        # Trạng thái ID (Dùng khi sửa/ẩn)
        self.lbl_selected_id = tk.Label(frame_form, text="", bg="#f4f6f9", fg="#f4f6f9")
        self.lbl_selected_id.grid(row=0, column=4, padx=5)

        # --- Khu vực Nút bấm ---
        frame_btn = tk.Frame(self, bg="#f4f6f9")
        frame_btn.pack(fill="x", padx=20, pady=5)

        tk.Button(frame_btn, text="Thêm Mới", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=12, command=self.add_book).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Cập Nhật", bg="#f39c12", fg="white", font=("Arial", 10, "bold"), width=12, command=self.edit_book).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Làm Mới Form", bg="#95a5a6", fg="white", font=("Arial", 10, "bold"), width=12, command=self.clear_form).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Đăng Xuất", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=10, command=self.logout).pack(side="right", padx=5)

        # --- Khu vực Bảng Dữ liệu (Treeview) ---
        columns = ("ID", "Tên sách", "Tác giả")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Tên sách", text="Tên sách")
        self.tree.heading("Tác giả", text="Tác giả")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Tên sách", width=350)
        self.tree.column("Tác giả", width=200)
        
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        # Tải dữ liệu lần đầu
        self.load_data()

    def load_data(self):
        # Xóa dữ liệu cũ trên Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Lấy dữ liệu từ SQLite
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author FROM books")
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            self.tree.insert("", "end", values=row)

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        
        values = self.tree.item(selected, 'values')
        self.clear_form()
        
        # Đổ dữ liệu lên form
        self.lbl_selected_id.config(text=values[0])
        self.ent_title.insert(0, values[1])
        self.ent_author.insert(0, values[2])

    def add_book(self):
        title = self.ent_title.get().strip()
        author = self.ent_author.get().strip()
        
        if not title or not author:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ Tên sách và Tác giả!")
            return
            
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        conn.commit()
        conn.close()
        
        self.load_data()
        self.clear_form()
        messagebox.showinfo("Thành công", "Đã thêm sách mới!")

    def edit_book(self):
        book_id = self.lbl_selected_id.cget("text")
        title = self.ent_title.get().strip()
        author = self.ent_author.get().strip()
        
        if not book_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một sách từ bảng để sửa!")
            return
        if not title or not author:
            messagebox.showwarning("Cảnh báo", "Không được để trống Tên sách và Tác giả!")
            return
            
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET title=?, author=? WHERE id=?", (title, author, book_id))
        conn.commit()
        conn.close()
        
        self.load_data()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin sách!")

    def clear_form(self):
        self.ent_title.delete(0, 'end')
        self.ent_author.delete(0, 'end')
        self.lbl_selected_id.config(text="")

    def logout(self):
        # 1. Tùy chọn: Hiển thị hộp thoại xác nhận đăng xuất
        response = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất không?")
        
        if response:
            # 2. Xóa giao diện thủ thư hiện tại
            self.destroy() 
            
            # 3. Gọi lại hàm hiển thị màn hình đăng nhập từ controller (main.py)
            self.controller.show_login_screen()