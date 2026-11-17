import tkinter as tk
from tkinter import messagebox
import models
from gui_librarian import LibrarianDashboard
from gui_reader import ReaderDashboard

class AppController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Thư Viện")
        self.geometry("920x600")
        self.eval('tk::PlaceWindow . center')
        
        models.init_db()
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.current_frame = None
        self.show_login_screen()

    def show_login_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self.container, self)
        self.current_frame.pack(fill="both", expand=True)
        
    def show_librarian_dashboard(self, role="librarian"):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LibrarianDashboard(self.container, self, role)
        self.current_frame.pack(fill="both", expand=True)

    def show_reader_dashboard(self, role="reader"):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ReaderDashboard(self.container, self, role)
        self.current_frame.pack(fill="both", expand=True)


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f4f6f9")
        
        tk.Label(self, text="HỆ THỐNG THƯ VIỆN", font=("Arial", 22, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(pady=50)

        frame_form = tk.Frame(self, bg="#f4f6f9")
        frame_form.pack(pady=10)
        
        tk.Label(frame_form, text="Tài khoản:", font=("Arial", 11), bg="#f4f6f9").grid(row=0, column=0, padx=5, pady=10, sticky="e")
        self.ent_user = tk.Entry(frame_form, width=30, font=("Arial", 11))
        self.ent_user.grid(row=0, column=1, padx=5, pady=10)
        self.ent_user.insert(0, "admin")

        tk.Label(frame_form, text="Mật khẩu:", font=("Arial", 11), bg="#f4f6f9").grid(row=1, column=0, padx=5, pady=10, sticky="e")
        self.ent_pass = tk.Entry(frame_form, width=30, show="*", font=("Arial", 11))
        self.ent_pass.grid(row=1, column=1, padx=5, pady=10)
        self.ent_pass.insert(0, "123456")

        tk.Button(self, text="Đăng Nhập", bg="#2980B9", fg="white", font=("Arial", 12, "bold"), width=18,
                  command=self.handle_login).pack(pady=20)
                  
        tk.Label(self, text="Tài khoản mẫu: admin / 123456 (Thủ thư)  |  student / 123456 (Độc giả)", 
                 font=("Arial", 9, "italic"), bg="#f4f6f9", fg="#7f8c8d").pack(pady=10)

    def handle_login(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()
        
        role = models.verify_login(user, pwd)
        if role == 'librarian':
            self.controller.show_librarian_dashboard(role)
        elif role == 'reader':
            self.controller.show_reader_dashboard(role)
        else:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu!")

if __name__ == "__main__":
    app = AppController()
    app.mainloop()
