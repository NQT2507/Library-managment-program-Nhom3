import customtkinter as ctk
from tkinter import ttk
import os
from PIL import Image, ImageTk

class ReaderDashboard(ctk.CTkFrame):
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

        self.canvas.create_text(450, 60, text="XIN CHÀO ĐỘC GIẢ", font=("Segoe UI", 28, "bold"), fill="white")
        
        # Khung làm việc
        work_frame = ctk.CTkFrame(self, width=800, height=450, corner_radius=15)
        work_frame.place(relx=0.5, rely=0.55, anchor="center")

        # Khung Tìm kiếm
        search_frame = ctk.CTkFrame(work_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.ent_search = ctk.CTkEntry(search_frame, placeholder_text="Nhập tên sách hoặc tác giả...", width=300)
        self.ent_search.pack(side="left", padx=5)
        
        ctk.CTkButton(search_frame, text="Tìm kiếm", width=100, font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)

        # Treeview styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=30,
                        fieldbackground="#343638", font=("Segoe UI", 11))
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", font=("Segoe UI", 12, "bold"))

        # Bảng
        columns = ("ID", "Tên sách", "Tác giả", "Thể loại")
        self.tree = ttk.Treeview(work_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Tên sách", width=350)
        self.tree.column("Tác giả", width=200)
        self.tree.column("Thể loại", width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Đăng xuất
        btn_frame = ctk.CTkFrame(work_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(btn_frame, text="Đăng xuất", fg_color="#E74C3C", hover_color="#C0392B", 
                      font=("Segoe UI", 12, "bold"), command=self.logout).pack(side="right")

    def logout(self):
        self.controller.show_login_screen()
