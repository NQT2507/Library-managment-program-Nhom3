import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import models

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Đăng nhập - Quản lý Thư viện")
        self.root.geometry("400x250")
        self.root.eval('tk::PlaceWindow . center')
        

        models.init_db()

        tk.Label(root, text="HỆ THỐNG THƯ VIỆN", font=("Segoe UI", 16, "bold")).pack(pady=20)


        frame = tk.Frame(root)
        frame.pack(pady=10)
        
        tk.Label(frame, text="Tài khoản:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_user = tk.Entry(frame, width=25)
        self.ent_user.grid(row=0, column=1, padx=5, pady=5)
        self.ent_user.insert(0, "admin")

        tk.Label(frame, text="Mật khẩu:").grid(row=1, column=0, padx=5, pady=5)
        self.ent_pass = tk.Entry(frame, width=25, show="*")
        self.ent_pass.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(root, text="Đăng Nhập", bg="#2980B9", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.handle_login).pack(pady=10)

    def handle_login(self):
        user = self.ent_user.get()
        pwd = self.ent_pass.get()
        
        role = models.verify_login(user, pwd)
        if role:
            messagebox.showinfo("Thành công", f"Đăng nhập thành công với quyền: {role.upper()}")
            self.root.destroy()
            

            main_root = tk.Tk()
            MainApp(main_root, role)
            main_root.mainloop()
        else:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu!")

class MainApp:
    def __init__(self, root, role):
        self.root = root
        self.root.title("Bảng Điều Khiển Thư Viện")
        self.root.geometry("800x500")

        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        bg_path = os.path.join(assets_dir, "bg_main.jpg")
        
        self.canvas = tk.Canvas(self.root, width=800, height=500)
        self.canvas.pack(fill="both", expand=True)

        try:
            img = Image.open(bg_path).resize((800, 500))
            self.bg = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.bg, anchor="nw")
        except FileNotFoundError:

            self.canvas.configure(bg="#2C3E50") 


        self.canvas.create_text(400, 50, text=f"XIN CHÀO THỦ THƯ", font=("Segoe UI", 24, "bold"), fill="white")
        

        work_frame = tk.Frame(self.root, bg="white")
        work_frame.place(relx=0.5, rely=0.55, anchor="center", width=700, height=350)
        

        columns = ("ID", "Tên sách", "Tác giả")
        self.tree = ttk.Treeview(work_frame, columns=columns, show="headings")
        self.tree.heading("ID", text="Mã sách")
        self.tree.heading("Tên sách", text="Tên sách")
        self.tree.heading("Tác giả", text="Tác giả")
        
        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Tên sách", width=350)
        self.tree.column("Tác giả", width=250)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)


        btn_frame = tk.Frame(work_frame, bg="white")
        btn_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_frame, text="+ Thêm Đầu Sách", bg="#27AE60", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Tải lại bảng", bg="#8E44AD", fg="white").pack(side="left", padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()