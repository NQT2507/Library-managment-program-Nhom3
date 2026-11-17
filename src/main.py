import customtkinter as ctk
from tkinter import messagebox
import models
from gui_librarian import LibrarianDashboard
from gui_reader import ReaderDashboard

# Cài đặt giao diện mặc định
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Quản Lý Thư Viện")
        self.root.resizable(False, False)
        
        models.init_db()
        self.current_frame = None
        self.show_login_screen()

    def switch_frame(self, frame_class, *args):
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        self.current_frame = frame_class(self.root, self, *args)
        self.current_frame.pack(fill="both", expand=True)

    def show_login_screen(self):
        self.root.geometry("450x300")
        self.switch_frame(LoginFrame)

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Tiêu đề
        self.lbl_title = ctk.CTkLabel(self, text="HỆ THỐNG THƯ VIỆN", font=("Segoe UI", 20, "bold"))
        self.lbl_title.pack(pady=20)

        # Khung chứa Form
        self.form_box = ctk.CTkFrame(self, width=350, height=200, corner_radius=10)
        self.form_box.pack(pady=10)

        # Input Tài khoản
        self.ent_user = ctk.CTkEntry(self.form_box, width=250, placeholder_text="Tài khoản")
        self.ent_user.pack(pady=12, padx=10)
        self.ent_user.insert(0, "admin")

        # Input Mật khẩu
        self.ent_pass = ctk.CTkEntry(self.form_box, width=250, placeholder_text="Mật khẩu", show="*")
        self.ent_pass.pack(pady=12, padx=10)

        # Nút Đăng nhập
        self.btn_login = ctk.CTkButton(self.form_box, text="Đăng Nhập", width=250, 
                                       font=("Segoe UI", 14, "bold"), command=self.handle_login)
        self.btn_login.pack(pady=15, padx=10)

    def handle_login(self):
        user = self.ent_user.get()
        pwd = self.ent_pass.get()
        
        role = models.verify_login(user, pwd)
        if role:
            self.controller.root.geometry("900x600")
            if role == 'librarian':
                self.controller.switch_frame(LibrarianDashboard, role)
            else:
                self.controller.switch_frame(ReaderDashboard, role)
        else:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu!")

if __name__ == "__main__":
    root = ctk.CTk()
    app = LibraryApp(root)
    root.mainloop()
