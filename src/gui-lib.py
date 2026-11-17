import customtkinter as ctk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import models

class LibrarianDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller, role):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # --- Canvas + Pillow ---
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        bg_path = os.path.join(assets_dir, "bg_main.jpg")
        
        self.canvas = ctk.CTkCanvas(self, width=900, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        try:
            img = Image.open(bg_path).resize((900, 600))
            self.bg = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.bg, anchor="nw")
        except FileNotFoundError:
            self.canvas.configure(bg="#2b2b2b")

        self.canvas.create_text(450, 60, text="XIN CHÀO THỦ THƯ", font=("Segoe UI", 28, "bold"), fill="white")
        
        # Khung làm việc
        work_frame = ctk.CTkFrame(self, width=800, height=450, corner_radius=15)
        work_frame.place(relx=0.5, rely=0.55, anchor="center")

        # --- Form nhập liệu (FR02) ---
        form_frame = ctk.CTkFrame(work_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=10)

        # Hàng 1
        ctk.CTkLabel(form_frame, text="ISBN:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_isbn = ctk.CTkEntry(form_frame, width=150)
        self.ent_isbn.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Tên sách:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.ent_title = ctk.CTkEntry(form_frame, width=250)
        self.ent_title.grid(row=0, column=3, padx=5, pady=5)

        # Hàng 2
        ctk.CTkLabel(form_frame, text="Tác giả:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_author = ctk.CTkEntry(form_frame, width=150)
        self.ent_author.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Mã thể loại:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.ent_cat = ctk.CTkEntry(form_frame, width=100)
        self.ent_cat.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        self.lbl_selected_id = ctk.CTkLabel(form_frame, text="")
        self.lbl_selected_id.grid(row=0, column=4, rowspan=2, padx=10) # Ẩn ID sách đang chọn
        self.lbl_selected_id.grid_remove() 
        
        # --- Treeview styling ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=30,
                        fieldbackground="#343638", font=("Segoe UI", 11))
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", font=("Segoe UI", 12, "bold"))

        # Bảng
        columns = ("ID", "ISBN", "Tên sách", "Tác giả", "Mã TL", "Trạng thái")
        self.tree = ttk.Treeview(work_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("ISBN", width=100, anchor="center")
        self.tree.column("Tên sách", width=250)
        self.tree.column("Tác giả", width=150)
        self.tree.column("Mã TL", width=60, anchor="center")
        self.tree.column("Trạng thái", width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Bắt sự kiện click vào dòng trong bảng
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        # Nút điều khiển
        btn_frame = ctk.CTkFrame(work_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(btn_frame, text="+ Thêm Sách", fg_color="#27AE60", hover_color="#219150", 
                      font=("Segoe UI", 12, "bold"), command=self.add_book).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Sửa Sách", fg_color="#F39C12", hover_color="#D68910", 
                      font=("Segoe UI", 12, "bold"), command=self.edit_book).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Ẩn/Hiện", fg_color="#7f8c8d", hover_color="#95a5a6", 
                      font=("Segoe UI", 12, "bold"), command=self.toggle_hidden).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Làm mới form", fg_color="#34495E", hover_color="#2C3E50", 
                      font=("Segoe UI", 12, "bold"), command=self.clear_form).pack(side="left", padx=20)
                      
        ctk.CTkButton(btn_frame, text="Đăng xuất", fg_color="#E74C3C", hover_color="#C0392B", 
                      font=("Segoe UI", 12, "bold"), command=self.logout).pack(side="right", padx=10)

        # Load dữ liệu lần đầu
        self.load_data()

    def clear_form(self):
        self.ent_isbn.delete(0, 'end')
        self.ent_title.delete(0, 'end')
        self.ent_author.delete(0, 'end')
        self.ent_cat.delete(0, 'end')
        self.lbl_selected_id.configure(text="")

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, 'values')
        
        self.clear_form()
        self.lbl_selected_id.configure(text=values[0])
        self.ent_isbn.insert(0, values[1])
        self.ent_title.insert(0, values[2])
        self.ent_author.insert(0, values[3])
        self.ent_cat.insert(0, values[4])

    def load_data(self):
        # Xóa dữ liệu cũ trên bảng
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        import sqlite3
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, isbn, title, author, category_id, is_hidden FROM books")
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            status = "Đã ẩn" if row[5] == 1 else "Hiển thị"
            cat = row[4] if row[4] is not None else ""
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], cat, status))

    def add_book(self):
        isbn = self.ent_isbn.get().strip()
        title = self.ent_title.get().strip()
        author = self.ent_author.get().strip()
        cat = self.ent_cat.get().strip()
        
        if not isbn or not title or not author:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập ISBN, Tên sách và Tác giả.")
            return
            
        cat_val = int(cat) if cat.isdigit() else None
            
        import sqlite3
        try:
            conn = sqlite3.connect(models.DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (isbn, title, author, category_id) VALUES (?, ?, ?, ?)",
                           (isbn, title, author, cat_val))
            conn.commit()
            conn.close()
            self.load_data()
            self.clear_form()
            messagebox.showinfo("Thành công", "Đã thêm sách mới.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã ISBN đã tồn tại!")

    def edit_book(self):
        book_id = self.lbl_selected_id.cget("text")
        if not book_id:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một sách từ bảng để sửa.")
            return
            
        isbn = self.ent_isbn.get().strip()
        title = self.ent_title.get().strip()
        author = self.ent_author.get().strip()
        cat = self.ent_cat.get().strip()
        
        if not isbn or not title or not author:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập ISBN, Tên sách và Tác giả.")
            return
            
        cat_val = int(cat) if cat.isdigit() else None
            
        import sqlite3
        try:
            conn = sqlite3.connect(models.DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE books SET isbn=?, title=?, author=?, category_id=? WHERE id=?",
                           (isbn, title, author, cat_val, book_id))
            conn.commit()
            conn.close()
            self.load_data()
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin sách.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã ISBN bị trùng lặp!")

    def toggle_hidden(self):
        book_id = self.lbl_selected_id.cget("text")
        if not book_id:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một sách từ bảng để thao tác.")
            return
            
        import sqlite3
        conn = sqlite3.connect(models.DB_PATH)
        cursor = conn.cursor()
        
        # Kiểm tra trạng thái hiện tại
        cursor.execute("SELECT is_hidden FROM books WHERE id=?", (book_id,))
        current_status = cursor.fetchone()[0]
        
        # Đảo ngược trạng thái
        new_status = 1 if current_status == 0 else 0
        
        cursor.execute("UPDATE books SET is_hidden=? WHERE id=?", (new_status, book_id))
        conn.commit()
        conn.close()
        
        self.load_data()

    def logout(self):
        self.controller.show_login_screen()