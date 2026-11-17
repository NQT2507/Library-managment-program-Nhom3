
# Ứng dụng Desktop quản lý thư viện
Bài tập lớn / Đồ án môn học viết bằng Python (Tkinter) và SQLite.

## Chức năng chính

- **Đăng nhập & Phân quyền:** Chia 2 vai trò Thủ thư (`librarian`) và Độc giả (`reader`), mật khẩu mã hóa SHA-256.
- **Thủ thư:**
  - Thêm, sửa, ẩn/hiện đầu sách và phân loại theo danh mục.
  - Quản lý số lượng bản sao vật lý của từng đầu sách.
  - Lập phiếu mượn (tự động kiểm tra sách còn trong kho) và ghi nhận trả sách.
  - Lọc danh sách các phiếu mượn bị quá hạn.
- **Độc giả:**
  - Tìm kiếm sách theo tên, tác giả hoặc lọc theo thể loại.
  - Xem số lượng sách hiện còn sẵn tại thư viện.

## Cấu trúc thư mục

- `src/`: Mã nguồn giao diện (`main.py`, `gui_librarian.py`, `gui_reader.py`) và xử lý dữ liệu (`models.py`).
- `database/`: Chứa file cơ sở dữ liệu SQLite (`library.db`).
- `assets/`: Chứa hình ảnh giao diện.

## Cách chạy chương trình

Mở terminal tại thư mục gốc của dự án và chạy lệnh:
```bash
git clone https://github.com/NQT2507/Library-managment-program.git
cd Library-managment-program
pip install Pillow
python src/main.py
```
## ghi chú
Cá nhân sử dụng trợ lý AI claude để hỗ trợ rà soát cấu trúc mã nguồn, gợi ý bố cục giao diện Tkinter và chuẩn hóa tài liệu; sinh viên đã tự đọc hiểu, chạy kiểm thử thực tế và chịu trách nhiệm toàn bộ nội dung nộp.