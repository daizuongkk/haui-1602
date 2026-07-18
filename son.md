# Thiết kế Notification Service cho hệ thống cảnh báo thiên tai

## 1. Mục tiêu

Sau khi hệ thống dự báo sinh ra cảnh báo dưới dạng JSON, Notification Service sẽ:

1. Nhận cảnh báo.
2. Xác định khu vực bị ảnh hưởng.
3. Lấy danh sách người dân trong khu vực từ CSDL.
4. Xác định ngôn ngữ nhận thông báo của từng người.
5. Sinh nội dung phù hợp với từng ngôn ngữ.
6. Gửi thông báo qua Zalo Official Account.
7. Ghi log kết quả gửi.

---

# 2. Kiến trúc tổng thể

```text
               Hệ thống dự báo
                      │
          Sinh cảnh báo (JSON)
                      │
                      ▼
          Notification Service
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   Citizen Database          Translation Service
          │                       │
          └───────────┬───────────┘
                      ▼
               Zalo OA API
                      │
                      ▼
                 Người dân
```

---

# 3. Luồng xử lý

```text
Hệ thống dự báo
      │
      ▼
Sinh cảnh báo JSON
      │
      ▼
Notification Service
      │
      ▼
Lấy thông tin khu vực
      │
      ▼
Truy vấn CSDL người dân
      │
      ▼
Lấy danh sách người nhận
      │
      ▼
Xác định ngôn ngữ
      │
      ▼
Sinh nội dung theo ngôn ngữ
      │
      ▼
Gửi Zalo OA
      │
      ▼
Lưu log
```

---

# 4. Thiết kế JSON cảnh báo

Ví dụ:

```json
{
    "warning_id": "W20260601001",
    "type": "Mưa lớn",
    "level": 3,
    "province": "Hà Giang",
    "district": "Đồng Văn",
    "ward": "Lũng Cú",
    "start_time": "2026-06-01T14:00:00",
    "end_time": "2026-06-01T18:00:00",
    "content": "Dự báo mưa lớn từ 50-100mm."
}
```

---

# 5. Thiết kế CSDL người dân

## Bảng citizens

| Cột | Ý nghĩa |
|------|----------|
| id | ID |
| full_name | Họ tên |
| phone | SĐT |
| zalo_user_id | ID Zalo |
| province | Tỉnh |
| district | Huyện |
| ward | Xã |
| ethnicity | Dân tộc |
| language | Ngôn ngữ nhận thông báo |
| receive_warning | Có nhận cảnh báo hay không |

Ví dụ

| full_name | province | district | ethnicity | language |
|------------|----------|----------|------------|----------|
| A | Hà Giang | Đồng Văn | H'Mông | hmn |
| B | Hà Giang | Đồng Văn | Dao | dao |
| C | Hà Giang | Đồng Văn | Kinh | vi |

---

# 6. Truy vấn người nhận

Ví dụ SQL

```sql
SELECT *
FROM citizens
WHERE province='Hà Giang'
AND district='Đồng Văn'
AND receive_warning=true;
```

---

# 7. Xử lý ngôn ngữ

Nếu language

```
vi
```

thì gửi tiếng Việt.

Nếu

```
hmn
```

thì gửi tiếng H'Mông.

Nếu

```
dao
```

thì gửi tiếng Dao.

---

# 8. Sinh nội dung

Có hai phương án.

## Phương án 1

AI sinh nhiều bản dịch.

```json
{
    "vi":"Cảnh báo mưa lớn...",
    "hmn":"...",
    "dao":"..."
}
```

Notification Service chỉ cần chọn.

---

## Phương án 2

AI chỉ sinh tiếng Việt.

Notification Service gọi Translation Service.

```
Tiếng Việt
      │
      ▼
Translation Service
      │
      ▼
Tiếng H'Mông
```

---

# 9. Gửi Zalo OA

Notification Service gửi

```
POST /oa/message
```

Body

```json
{
    "recipient":{
        "user_id":"123456789"
    },
    "message":{
        "text":"⚠️ Cảnh báo mưa lớn..."
    }
}
```

---

# 10. Ghi log

Tạo bảng

```
notification_logs
```

| Cột |
|------|
| id |
| citizen_id |
| warning_id |
| send_time |
| language |
| status |
| response |

Ví dụ

| citizen | status |
|----------|--------|
| A | SUCCESS |
| B | FAILED |

---

# 11. Chống gửi trùng

Kiểm tra

```
warning_id
+
citizen_id
```

Nếu đã gửi

```
Không gửi lại.
```

---

# 12. Pseudocode

```python
warning = receive_warning()

citizens = find_citizens(
    province=warning.province,
    district=warning.district
)

for citizen in citizens:

    language = citizen.language

    message = translate(
        warning.content,
        language
    )

    send_zalo(
        citizen.zalo_user_id,
        message
    )

    save_log()
```

---

# 13. API nội bộ

## POST /warning

Input

```json
{
    "warning_id":"...",
    "province":"...",
    "district":"...",
    "content":"..."
}
```

Response

```json
{
    "status":"received"
}
```

---

# 14. Các module cần phát triển

```
notification-service
│
├── controller
│      Nhận cảnh báo
│
├── service
│      Điều phối xử lý
│
├── citizen
│      Truy vấn CSDL
│
├── translator
│      Dịch nội dung
│
├── zalo
│      Gửi OA API
│
├── repository
│      Đọc/Ghi Database
│
└── log
       Lưu lịch sử gửi
```

---

# 15. Trình tự xử lý

```text
Forecast System
      │
      ▼
POST /warning
      │
      ▼
Notification Service
      │
      ▼
Đọc JSON
      │
      ▼
Xác định khu vực
      │
      ▼
Truy vấn CSDL
      │
      ▼
Lấy người nhận
      │
      ▼
Lặp qua từng người
      │
      ├── lấy language
      ├── dịch
      ├── gửi Zalo
      └── ghi log
      │
      ▼
Hoàn thành
```

---

# 16. Hướng mở rộng

- Gửi SMS nếu người dân chưa sử dụng Zalo.
- Gửi Email cho cơ quan địa phương.
- Gửi thông báo qua ứng dụng di động.
- Hỗ trợ nhiều mô hình dịch tự động.
- Hàng đợi (RabbitMQ/Kafka) để xử lý hàng nghìn thông báo đồng thời.
- Dashboard theo dõi trạng thái gửi và thống kê tỷ lệ thành công.