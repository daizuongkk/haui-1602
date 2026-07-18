# Thiết kế Notification Service cho hệ thống cảnh báo thiên tai (Phiên bản Cập nhật cho Claude)

## 1. Mục tiêu

Xây dựng module **Notification Service** làm nhiệm vụ đọc các bản tin cảnh báo đã được dịch (trong file `alert.json`), truy xuất cơ sở dữ liệu `dienbien_weather` để tìm người dân trong vùng ảnh hưởng, và tiến hành **Gửi Email Thực Tế**.

Quy trình ưu tiên:
1. Ưu tiên theo mức độ cảnh báo của vùng (Red -> Orange -> Yellow).
2. Ưu tiên theo độ tuổi của người nhận (Người lớn tuổi và trẻ nhỏ được gửi trước).
3. Gửi nội dung đúng ngôn ngữ (`dan_toc`) tới email của người dân.

---

## 2. Kiến trúc tổng thể

```text
    alert.json (Đã chứa sẵn bản dịch 3 ngôn ngữ)
                       │
                       ▼
             Notification Service
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
  SQL Server Database       Module Gửi Tin
  - nguoi_dan               - GỬI EMAIL THẬT (smtplib)
  - notification_logs       
```

---

## 3. Luồng xử lý chi tiết (Priority Queue)

1. **Khởi tạo & Đọc dữ liệu**: 
   - Đọc danh sách cảnh báo từ `alert.json`.
   - Sắp xếp mảng cảnh báo theo `highest_alert_level` (Red > Orange > Yellow).
2. **Quét Database theo Vùng (Chế độ TEST)**: 
   - Với mỗi cảnh báo, truy vấn bảng `nguoi_dan` khớp với `huyen`.
   - Lọc lấy những người có `nhan_canh_bao = 1`.
   - **Đặc biệt lưu ý**: Để test an toàn, hãy giới hạn kết quả lấy ra chỉ gồm **5 người dùng đầu tiên** (VD: thêm điều kiện `WHERE id <= 5` hoặc `TOP 5`) để chỉ gửi mail vào 5 email thật mà user đã điền, tránh gửi mail rác đến 45 địa chỉ fake phía sau.
3. **Phân loại mức độ ưu tiên (Sorting)**:
   - Sắp xếp 5 đối tượng trên: 
     - Nhóm 1: Tuổi (`tuoi`) >= 60 hoặc Tuổi <= 12.
     - Nhóm 2: Các độ tuổi còn lại.
4. **Cá nhân hóa và Gửi tin**:
   - Duyệt qua từng người dân (đã sort).
   - **Chống trùng**: Kiểm tra nếu `nguoi_dan_id` và `warning_id` (tạo bằng `{location}_{date}`) đã tồn tại trong bảng `notification_logs` thì bỏ qua.
   - Chọn bản dịch tương ứng từ object `messages` dựa vào `dan_toc` (Kinh -> `vi`, Thái -> `thai`, HMong -> `hmong`).
   - **Thực thi gửi Email**: Gọi hàm Python `smtplib` để **gửi Email thật** đến địa chỉ `email`.
   - Insert bản ghi vào bảng `notification_logs` với status `SUCCESS` hoặc `FAILED`.

---

## 4. Thiết kế Cơ sở dữ liệu (SQL Server)

Sử dụng `pyodbc` để thao tác với SQL Server (Database: `dienbien_weather`).

### Bảng `nguoi_dan` (Sẽ được tạo từ file SQL có sẵn)

| Cột | Kiểu | Mô tả |
|------|----------|----------|
| `id` | `INT IDENTITY(1,1)` | Khóa chính |
| `ho_ten` | `VARCHAR(100)` | Họ và tên |
| `so_dien_thoai` | `VARCHAR(10)` | Số điện thoại |
| `huyen` | `VARCHAR(50)` | Huyện (Khớp với `location` trong alert.json) |
| `dan_toc` | `VARCHAR(20)` | Dân tộc (Kinh/Thái/HMong) |
| `tuoi` | `INT` | Tuổi (dùng để xếp ưu tiên) |
| `zalo_id` | `VARCHAR(50)` | ID Zalo |
| `email` | `VARCHAR(100)` | Địa chỉ Email (Dùng để nhận cảnh báo thực tế) |
| `nhan_canh_bao` | `BIT` | Cờ cho phép nhận tin (1 = Có) |

### Bảng `notification_logs` (Cần tạo thêm)

| Cột | Kiểu | Mô tả |
|------|------|----------|
| `id` | `INT IDENTITY(1,1)` | Khóa chính |
| `nguoi_dan_id` | `INT` | ID người nhận (Foreign Key -> nguoi_dan.id) |
| `warning_id` | `VARCHAR(100)` | ID cảnh báo (VD: `Huyện Mường Nhé_17/07/2026`) |
| `send_time` | `DATETIME` | Thời điểm gửi |
| `status` | `VARCHAR(20)` | Trạng thái (`SUCCESS`, `FAILED`) |

---

## 5. Yêu cầu Code dành cho Claude

Vui lòng viết file Python hoàn chỉnh sau:

### 1. `db_setup.py`
- Kết nối SQL Server qua `pyodbc`.
- **Thực thi trực tiếp toàn bộ nội dung của file `dienbien_weather_updated.sql`** để tạo database `dienbien_weather`, bảng `nguoi_dan` và nạp 50 dữ liệu (trong đó 5 dòng đầu user đã tự đổi thành email thật).
- Xóa và tạo bảng `notification_logs`.

### 2. `notification_service.py`
- Kết nối SQL Server Database `dienbien_weather` qua `pyodbc`.
- Triển khai logic đã nêu ở mục 3:
  - Phải có cơ chế **TEST MODE**: Chỉ quét và xử lý gửi tin cho **5 người dùng có ID từ 1 đến 5**. (Hoặc `TOP 5`). Mục đích là để ngăn việc cố gắng gửi hàng chục email rác làm chậm/crash hệ thống.
  - Sort ưu tiên tuổi -> Map dân tộc với ngôn ngữ -> Gửi log.
- **Tính năng Gửi Email thật**: 
  - Viết hàm `send_email_alert(to_email, subject, body)` sử dụng thư viện `smtplib` và `email.mime`. 
  - Sử dụng config SMTP từ file `.env` (Biến: `SMTP_SERVER`, `SMTP_PORT`, `SENDER_EMAIL`, `SENDER_PASSWORD`). Bắt khối try-except để nếu gửi lỗi (VD: sai pass) thì vẫn ghi log là `FAILED` chứ không sập cả chương trình.
- Xử lý mượt mà việc kết nối SQL, truy xuất và đóng kết nối.
