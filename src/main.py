import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import models

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Đăng nhập - Quản lý Thư viện")
        self.root.geometry("450x300")
        self.root.eval('tk::PlaceWindow . center')
        self.root.resizable(False, False)
        
        models.init_db()

        self.lbl_title = ctk.CTkLabel(root, text="HỆ THỐNG THƯ VIỆN", font=("Segoe UI", 20, "bold"))
        self.lbl_title.pack(pady=20)

        self.frame = ctk.CTkFrame(root, width=350, height=200, corner_radius=10)
        self.frame.pack(pady=10)

        self.ent_user = ctk.CTkEntry(self.frame, width=250, placeholder_text="Tài khoản")
        self.ent_user.pack(pady=12, padx=10)
        self.ent_user.insert(0, "admin")

        self.ent_pass = ctk.CTkEntry(self.frame, width=250, placeholder_text="Mật khẩu", show="*")
        self.ent_pass.pack(pady=12, padx=10)

        self.btn_login = ctk.CTkButton(self.frame, text="Đăng Nhập", width=250, 
                                       font=("Segoe UI", 14, "bold"), command=self.handle_login)
        self.btn_login.pack(pady=15, padx=10)

    def handle_login(self):
        user = self.ent_user.get()
        pwd = self.ent_pass.get()
        
        role = models.verify_login(user, pwd)
        if role:
            self.root.destroy() 
            
            main_root = ctk.CTk()
            MainApp(main_root, role)
            main_root.mainloop()
        else:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu!")

class MainApp:
    def __init__(self, root, role):
        self.root = root
        self.root.title("Bảng Điều Khiển Thư Viện")
        self.root.geometry("900x600")
        

        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        bg_path = os.path.join(assets_dir, "bg_main.jpg")
        
        self.canvas = ctk.CTkCanvas(self.root, width=900, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        try:
            img = Image.open(bg_path).resize((900, 600))
            self.bg = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.bg, anchor="nw")
        except FileNotFoundError:
            self.canvas.configure(bg="#2b2b2b")


        role_name = "THỦ THƯ" if role == "librarian" else "ĐỘC GIẢ"
        self.canvas.create_text(450, 60, text=f"XIN CHÀO {role_name}", 
                                font=("Segoe UI", 28, "bold"), fill="white")
        

        work_frame = ctk.CTkFrame(self.root, width=800, height=450, corner_radius=15)

        work_frame.place(relx=0.5, rely=0.55, anchor="center")
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=30,
                        fieldbackground="#343638",
                        font=("Segoe UI", 11))
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", 
                        background="#565b5e", 
                        foreground="white", 
                        font=("Segoe UI", 12, "bold"))


        columns = ("ID", "Tên sách", "Tác giả")
        self.tree = ttk.Treeview(work_frame, columns=columns, show="headings")
        self.tree.heading("ID", text="Mã sách")
        self.tree.heading("Tên sách", text="Tên sách")
        self.tree.heading("Tác giả", text="Tác giả")
        
        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Tên sách", width=400)
        self.tree.column("Tác giả", width=250)
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)


        btn_frame = ctk.CTkFrame(work_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        

        ctk.CTkButton(btn_frame, text="+ Thêm Sách", fg_color="#27AE60", hover_color="#219150", 
                      font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Sửa Sách", fg_color="#F39C12", hover_color="#D68910", 
                      font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Tải lại bảng", fg_color="#8E44AD", hover_color="#732D91", 
                      font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)

if __name__ == "__main__":
    root = ctk.CTk()
    app = LoginWindow(root)
    root.mainloop()