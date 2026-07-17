# AI Agent Specification v2 - Multilingual Weather Alert Generator

## Mục tiêu

Xây dựng một AI Agent có nhiệm vụ:

* Nhận dữ liệu dự báo thời tiết dạng JSON.
* Gọi Gemini 2.5 Pro.
* Sinh bản tin cảnh báo bằng:

  * Tiếng Việt
  * Tiếng Thái (Điện Biên)
  * Tiếng H'Mông (Việt Nam)
* Xuất ra một file JSON chuẩn (`alert.json`).

**Lưu ý:** Agent **không** thực hiện gửi SMS, Zalo hoặc thông báo. Đó là trách nhiệm của các service khác trong hệ thống.

---

# Kiến trúc

```text
Forecast Model
      │
      ▼
forecast.json
      │
      ▼
AI Agent
      │
      ▼
Validation
      │
      ▼
Forecast Log (PostgreSQL)
      │
      ▼
Translation Cache
      │
      ├───────────────┐
      │ Cache Hit     │
      ▼               │
 Return alert.json    │
                      │
                      ▼
              Gemini 2.5 Pro
                      │
                      ▼
             Response Validation
                      │
                      ▼
        Alert Log (PostgreSQL)
                      │
                      ▼
               alert.json
```

---

# Trách nhiệm của Agent

Agent chỉ chịu trách nhiệm:

1. Đọc `forecast.json`
2. Kiểm tra dữ liệu đầu vào
3. Lưu Forecast Log
4. Kiểm tra Translation Cache
5. Nếu cache không tồn tại:

   * Gọi Gemini 2.5 Pro
6. Validate phản hồi
7. Lưu Alert Log
8. Sinh `alert.json`

Agent **không gửi SMS**.

Agent **không gửi Zalo**.

Agent **không gọi Notification Service**.

---

# Input

Input là file JSON dự báo.

Ví dụ:

```json
[
  {
    "location": "Huyện Mường Nhé",
    "date": "20/07/2026",
    "weather_summary": {},
    "alerts": []
  }
]
```

---

# Bước 1 - Input Validation

Kiểm tra:

* JSON hợp lệ
* Có location
* Có date
* Có alerts
* Không null
* Không lỗi parse

Nếu lỗi:

* Ghi log
* Dừng xử lý

---

# Bước 2 - Forecast Log

Lưu nguyên bản JSON đầu vào.

Ví dụ bảng:

```sql
forecast_logs

id
forecast_hash
forecast_json
created_at
```

Mục đích:

* Audit
* Debug
* Reproduce

---

# Bước 3 - Translation Cache

Sinh hash từ forecast JSON.

Ví dụ:

```text
SHA256(forecast_json)
```

Kiểm tra:

```text
Cache tồn tại?

YES
↓

Trả alert.json

NO
↓

Gọi Gemini
```

Mục tiêu:

* Giảm chi phí API.
* Giảm latency.
* Không dịch lại cùng một dữ liệu.

---

# Bước 4 - Gemini

Model:

```
gemini-2.5-pro
```

Temperature:

```
0.2
```

Response MIME Type:

```
application/json
```

---

# Prompt

Gemini phải:

* Chỉ sử dụng dữ liệu trong JSON.
* Không tự suy diễn.
* Không thay đổi số liệu.
* Không thay đổi mức cảnh báo.
* Không thêm hiện tượng thời tiết.
* Không thêm thông tin ngoài dữ liệu.

Nhiệm vụ:

1. Sinh bản tin tiếng Việt.
2. Dịch sang tiếng Thái.
3. Dịch sang tiếng H'Mông.
4. Trả đúng JSON.

---

# Output Schema

```json
{
  "location": "",
  "date": "",
  "highest_alert_level": "",
  "messages": {
    "vi": "",
    "thai": "",
    "hmong": ""
  }
}
```

Chỉ trả JSON.

Không Markdown.

Không giải thích.

---

# Bước 5 - Response Validation

Kiểm tra:

* Parse JSON thành công
* Có đủ field
* Có messages.vi
* Có messages.thai
* Có messages.hmong

Nếu lỗi:

Retry tối đa 2 lần.

Nếu vẫn lỗi:

Đánh dấu FAILED.

---

# Bước 6 - Alert Log (LLMOps)

Lưu toàn bộ phản hồi của Gemini.

Ví dụ bảng:

```sql
llm_outputs

id
forecast_hash
model_name
prompt
response_json
input_tokens
output_tokens
latency_ms
status
created_at
```

Mục đích:

* Theo dõi chất lượng dịch
* Debug
* Thống kê chi phí
* Audit

---

# Bước 7 - Translation Cache Update

Nếu phản hồi hợp lệ:

Lưu:

```text
forecast_hash

↓

alert.json
```

Những lần sau:

Không cần gọi Gemini.

---

# Bước 8 - Sinh alert.json

Ví dụ:

```json
{
  "location": "Huyện Mường Nhé",
  "date": "20/07/2026",
  "highest_alert_level": "Red",
  "messages": {
    "vi": "...",
    "thai": "...",
    "hmong": "..."
  }
}
```

Đây là output cuối cùng của Agent.

---

# Retry Policy

Retry khi:

* Timeout
* JSON lỗi
* Thiếu field
* Sai schema
* Gemini trả Markdown

Retry tối đa:

```
2 lần
```

---

# Environment Variables

```
GEMINI_API_KEY=

DATABASE_URL=
```

Không hard-code.

Không commit GitHub.

---

# Logging

Ghi log:

* Request time
* Response time
* Forecast hash
* Model
* Token usage
* Latency
* Success / Failed

---

# PostgreSQL Tables

## forecast_logs

```
id
forecast_hash
forecast_json
created_at
```

---

## llm_outputs

```
id
forecast_hash
model_name
prompt
response_json
input_tokens
output_tokens
latency_ms
status
created_at
```

---

## translation_cache

```
forecast_hash
alert_json
created_at
```

---

# Thư mục đề xuất

```
app/
│
├── agent/
│   ├── translator.py
│   ├── validator.py
│   ├── cache.py
│   ├── logger.py
│   └── prompt.py
│
├── database/
│   ├── models.py
│   ├── repository.py
│   └── migrations/
│
├── output/
│   └── alert.json
│
├── logs/
│
└── main.py
```

---

# Kết quả cuối cùng

AI Agent hoàn thành khi:

* Đọc được `forecast.json`.
* Gọi Gemini 2.5 Pro thành công.
* Sinh bản tin bằng:

  * Tiếng Việt
  * Tiếng Thái
  * Tiếng H'Mông.
* Validate kết quả.
* Lưu log vào PostgreSQL.
* Cache kết quả dịch.
* Xuất `alert.json`.

**Điểm kết thúc của Agent là `alert.json`. Mọi bước sau như SMS Gateway, Zalo OA, Web Dashboard hoặc Notification Service sẽ được xử lý bởi các module khác của hệ thống.**
