# Tài liệu Kiến trúc — Hệ thống AI Cảnh báo & Dự báo Thời tiết Vi mô Điện Biên

> **"Đúng người – Đúng lúc – Đúng ngôn ngữ"**
> Dự báo chi tiết cấp huyện/cụm bản · Cảnh báo tự động theo ngưỡng · Bản tin đa ngôn ngữ (Việt · Thái · H'Mông) · Phân phối đa kênh.

---

## 1. Tổng quan

Điện Biên có địa hình chia cắt mạnh, thời tiết cực đoan diễn ra nhanh (sương mù, lũ quét, sương muối, dông lốc) nhưng dự báo hiện chỉ ở cấp tỉnh — đến chậm, thiếu chi tiết cho từng vùng, và khó hiểu với đồng bào dân tộc thiểu số không đọc thạo tiếng phổ thông.

Hệ thống giải quyết bài toán bằng một **pipeline AI 4 lớp**, kết thúc ở hai giao diện người dùng: màn hình đơn giản cho người dân và dashboard giám sát cho Ban Chỉ huy PCTT.

```
┌────────────────────────────────────────────────────────────────────────┐
│  LỚP 1 · NGUỒN DỮ LIỆU                                                    │
│  Open-Meteo Forecast API · (mở rộng: OpenWeatherMap, Đài KTTV Điện Biên) │
└───────────────────────────────┬────────────────────────────────────────┘
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LỚP 2 · XỬ LÝ & MÔ HÌNH  (Python)                                        │
│  weather_service.py  → hạ độ phân giải nhiệt độ theo địa hình (lapse rate)│
│  rule_engine.py      → phát hiện 7 nhóm hiểm họa theo ngưỡng cấu hình     │
│  main.py             → điều phối → active_alerts.json                     │
└───────────────────────────────┬────────────────────────────────────────┘
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LỚP 3 · AI NGÔN NGỮ  (translation_agent/)                                │
│  LLM sinh bản tin + dịch Việt→Thái/H'Mông → output/alert.json            │
│  TTS (gTTS) → output/audio/<huyện>/<ngày>/<ngôn_ngữ>.mp3                  │
└───────────────────────────────┬────────────────────────────────────────┘
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LỚP 4 · API & PHÂN PHỐI  (backend/ FastAPI)                              │
│  Hợp nhất dữ liệu → REST API → mô phỏng SMS / Zalo OA / loa phát thanh    │
└───────────────────────────────┬────────────────────────────────────────┘
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  GIAO DIỆN NGƯỜI DÙNG  (frontend/ React + Vite)                           │
│  • Người dân: thang màu 4 cấp + icon + audio, hiểu không cần đọc chữ      │
│  • Ban PCTT: bản đồ cảnh báo, danh sách, chi tiết số liệu, gửi cảnh báo   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Nguồn dữ liệu (Data Sources)

| Nguồn | Hình thức | Tần suất | Vai trò |
|---|---|---|---|
| **Open-Meteo Forecast API** | REST, miễn phí, không cần key | Gọi 1–3h/lần (đề xuất cron) | Nguồn chính: 29 biến thời tiết theo giờ, dự báo 7 ngày |
| OpenWeatherMap (mở rộng) | REST, free tier | — | Nguồn dự phòng / đối chiếu |
| Đài KTTV Điện Biên (mở rộng) | Thủ công (Excel/CSV) hoặc API nếu có | — | Hiệu chỉnh bias theo quan trắc thực |
| Dữ liệu lịch sử thiên tai — Ban Chỉ huy PCTT (mở rộng) | File | — | Backtest & tinh chỉnh ngưỡng cảnh báo |

**Danh mục biến** khai báo tập trung tại `config/settings.py: WEATHER_VARIABLES` (nhiệt độ, mưa, gió giật, CAPE, độ ẩm đất nhiều tầng, tầm nhìn, mực đông lạnh, bốc thoát hơi…).

**Dự báo cấp xã/cụm xã:** đơn vị dự báo là **xã** (`data/communes.json`), sinh từ 3 huyện (`data/locations.json`) — mỗi xã có toạ độ + **độ cao thực riêng**, nên downscaling cho ra cảnh báo khác nhau giữa các xã cùng huyện. Thay `communes.json` bằng dữ liệu đo đạc thật là đủ để lên dữ liệu production (cấu trúc giữ nguyên).

---

## 3. Mô hình xử lý (Processing Model)

### 3.1 Hạ độ phân giải theo địa hình (downscaling)
Mô hình lưới của Open-Meteo (~9–11 km) không phản ánh đúng độ cao thực của từng xã vùng cao. `weather_service.downscale_temperature()` hiệu chỉnh nhiệt độ theo **gradient khí quyển** `LAPSE_RATE = 0.0065 °C/m`:

```
T_thực = T_mô_hình − LAPSE_RATE × (độ_cao_thực − độ_cao_lưới_mô_hình)
```

Đây là bước then chốt: mọi quyết định cảnh báo rét/sương muối đều dựa trên nhiệt độ **đã hiệu chỉnh**, không phải giá trị thô của API.

### 3.2 Bộ quy tắc phát hiện hiểm họa (Rule Engine)
`rule_engine.evaluate_hazards()` là hàm thuần, đánh giá **7 nhóm hiểm họa**, mỗi nhóm phân 3 mức **Vàng < Cam < Đỏ**:

1. Mưa lớn & Ngập úng 2. Lũ quét & Sạt lở 3. Dông, lốc, sét 4. Mưa đá
5. Sương muối & Băng giá 6. Rét đậm, rét hại 7. Sương mù dày đặc 8. Cháy rừng

Toàn bộ **ngưỡng để trong `config.py: THRESHOLDS`** (không hard-code trong logic) — điều chỉnh độ nhạy theo mùa/khu vực chỉ cần sửa bảng ngưỡng. Điểm nguy cơ sạt lở là công thức tổng hợp `mưa 24h · 0.5 + độ ẩm đất sâu · 150 + cân bằng nước · 0.3`, nhân hệ số rủi ro riêng từng huyện (`landslide_risk_factor`).

**Đánh giá chất lượng:** `benchmark.py` chạy 10 kịch bản lịch sử có nhãn (ground truth) và báo cáo POD (xác suất phát hiện), FAR (tỷ lệ báo động giả), CSI (chỉ số thành công) cho từng hiểm họa — dùng để kiểm tra hồi quy mỗi khi chỉnh ngưỡng.

### 3.3 Lớp AI ngôn ngữ
`translation_agent/` đọc `active_alerts.json`, gọi LLM sinh bản tin tiếng Việt chuẩn mực rồi dịch sang **tiếng Thái (phương ngữ Tai Dam/Tai Don Điện Biên)** và **H'Mông (chữ Latinh RPA)**. Prompt (`agent/prompt.py`) áp **ràng buộc chống bịa**: không đổi số liệu, không đổi mức cảnh báo, không thêm hiện tượng ngoài dữ liệu. Kết quả qua `agent/validator.py` (kiểm tra đủ trường + 3 ngôn ngữ) trong vòng lặp retry, xuất `output/alert.json`. `tts_reader.py` chuyển bản tin thành audio MP3.

### 3.4 Vòng phản hồi (Feedback loop — lộ trình)
Ghi nhận cảnh báo đúng/sai từ thực địa → hiệu chỉnh ngưỡng và hệ số bias theo thời gian.

---

## 4. Lớp API & Phân phối

### 4.1 REST API (`backend/`, FastAPI)
API hợp nhất **artifact JSON** (dữ liệu dự báo) với **DB trạng thái** (vòng đời cảnh báo).
Xác thực nhẹ cho thao tác của cán bộ qua header `X-Officer-Id`.

| Nhóm | Endpoint | Mô tả |
|---|---|---|
| Địa điểm | `GET /api/communes` (alias `/locations`) | Xã/cụm xã, nhóm theo huyện |
| Cán bộ | `GET /api/officers` | Danh sách cán bộ (chọn danh tính khi thao tác) |
| Tổng quan | `GET /api/summary` · `GET /api/dashboard/overview` | Mức cao nhất mỗi xã + KPI điều hành |
| Cảnh báo | `GET /api/alerts` · `GET /api/alerts/{id}` · `GET /api/forecast/{commune_id}` | Danh sách/chi tiết/chuỗi 3–7 ngày |
| Phê duyệt | `POST /api/alerts/{id}/approve\|reject` · `PATCH /api/alerts/{id}/status` | Cán bộ duyệt/từ chối/đổi trạng thái |
| Phân phối | `POST /api/alerts/{id}/dispatch` · `GET /api/alerts/{id}/dispatches` | Phát đa kênh (mô phỏng) + lịch sử |
| Phản hồi | `POST\|GET /api/alerts/{id}/feedback` | Người dân gửi & theo dõi phản hồi |
| Pipeline | `POST /api/pipeline/run` | Chạy fetch→đánh giá→dịch→TTS→lưu |
| Audio | `/audio/...` | Phục vụ file MP3 tĩnh (UTF-8) |

### 4.2 Kênh phân phối
| Kênh | Đối tượng | Định dạng |
|---|---|---|
| **Zalo OA / ZNS** | Cán bộ xã, dân có smartphone | Thẻ cảnh báo màu + bản tin + audio |
| **SMS** | Hộ dân không dùng app | Text ngắn có mã emoji cảnh báo |
| **Loa phát thanh xã** | Vùng lõm sóng / không đọc chữ | Audio 3 ngôn ngữ, phát lặp 3 lần |
| **Dashboard web** | Ban Chỉ huy PCTT tỉnh/huyện | Bản đồ + danh sách + chi tiết + điều phối |

> Ở bản demo, cả ba kênh SMS/Zalo/loa được **mô phỏng** qua adapter `MessageChannel`
> (`infrastructure/channels.py`) — mỗi lần phát **lưu một bản ghi `Dispatch`** (kênh, trạng
> thái `sent_sim`, nội dung, cán bộ). Tích hợp gửi thật = thay adapter, giữ nguyên interface.

### 4.3 Vòng đời cảnh báo & lưu trữ trạng thái (SQLite)

Ngoài artifact JSON (chỉ-đọc, ghi đè mỗi lần chạy pipeline), hệ thống có **CSDL trạng thái**
`data/app.db` (SQLAlchemy) là nguồn chân lý cho phê duyệt/phân phối/phản hồi:

```
pending_approval ──approve──► approved ──dispatch──► distributed ──close──► closed
       │                                                  ▲
       └──reject──► rejected ──(chạy lại)──► pending      └── feedback (không đổi status)
```

- **Bảng:** `alerts` (khóa tự nhiên `UNIQUE(commune_id, date)` → chạy lại là upsert, không nhân bản;
  nội dung đổi sau khi đã duyệt → tự đặt lại `pending_approval`), `dispatches`, `feedback`, `officers`.
- **Guard chuyển trạng thái** tập trung ở `shared/alert_status.py` — không phát cảnh báo chưa duyệt.
- **Phản hồi người dân** (`received`/`safe`/`need_help`) đổ về dashboard cán bộ (danh sách cần hỗ trợ).
- **Demo offline:** `python -m backend.presentation.cli seed` nạp dữ liệu cảnh báo thật vào DB ở
  trạng thái `pending_approval` → chạy được toàn bộ workflow không cần mạng/LLM.

---

## 5. Giao diện người dùng (`frontend/`, React + Vite)

Thiết kế **không phụ thuộc chữ viết**: mức nguy hiểm luôn thể hiện đồng thời bằng **màu + biểu tượng + nhãn**.

| Mức | Nhãn | Màu |
|---|---|---|
| 🟢 Green | Bình thường | `#2E7D32` |
| 🟡 Yellow | Chú ý | `#F9A825` |
| 🟠 Orange | Nguy hiểm | `#EF6C00` |
| 🔴 Red | Cực kỳ nguy hiểm | `#C62828` |

- **Màn hình Người dân** (mô phỏng điện thoại): chọn huyện → banner màu lớn + biểu tượng hiểm họa + trạng thái một từ → bản tin + nút nghe giọng nói (Việt/Thái/H'Mông) → pictogram hành động khuyến nghị → dải dự báo 7 ngày tô màu.
- **Dashboard Ban PCTT**: KPI theo mức → bản đồ sơ đồ hoá 3 huyện tô màu (offline, không cần tile ngoài) → danh sách cảnh báo → ngăn chi tiết (số liệu, hiểm họa, bản tin đa ngôn ngữ, audio) → nút mô phỏng phân phối đa kênh.

---

## 6. Công nghệ & Vận hành

- **Xử lý dữ liệu:** Python (thư viện chuẩn `urllib` cho API — không phụ thuộc HTTP ngoài).
- **AI ngôn ngữ:** LLM đa ngôn ngữ + `gTTS` cho TTS.
- **Backend:** FastAPI + Uvicorn (`backend/requirements.txt`).
- **Frontend:** React 18 + Vite 6; dev proxy `/api` & `/audio` → backend:8000.
- **Lưu trữ trạng thái:** SQLite + SQLAlchemy (`data/app.db`).
- **Chạy demo (offline, không cần mạng/LLM):**
  1. `pip install -r backend/requirements.txt`
  2. `python -m backend.presentation.cli seed` → tạo DB + 12 xã + cán bộ + cảnh báo demo (pending)
  3. `python -m uvicorn backend.presentation.api.app:app --reload` → API + `/docs`
  4. `cd frontend && npm install && npm run dev` → mở http://localhost:5173
- **Pipeline dữ liệu thật:** đặt `GEMINI_API_KEY` trong `.env` rồi gọi `POST /api/pipeline/run`
  (hoặc `python -m backend.presentation.cli` để chạy phần dự báo + xuất JSON).

---

## 7. Lộ trình triển khai (Deployment Roadmap)

| Giai đoạn | Thời gian | Mục tiêu |
|---|---|---|
| **Pilot** | Tháng 1–3 | Thử nghiệm 1 huyện trọng điểm (Mường Nhé); kết nối Đài KTTV lấy số liệu trạm thực; lập kênh Zalo OA với 5–10 xã |
| **Mở rộng & hiệu chỉnh** | Tháng 3–6 | Thu thập phản hồi đúng/sai; hiệu chỉnh downscaling bằng quan trắc thực; mở rộng toàn bộ huyện |
| **Đa ngôn ngữ chính thức** | Tháng 4–7 | Hợp tác giáo viên song ngữ xây bộ từ vựng cảnh báo chuẩn tiếng Thái/H'Mông; kiểm định chất lượng dịch |
| **Kết nối loa xã** | Tháng 6–9 | Tích hợp API hệ thống truyền thanh thông minh, tự động phát bản tin |
| **SMS chính thức & nhân rộng** | Tháng 9–12 | Hợp đồng nhà mạng cho SMS/cell broadcast khẩn cấp; đánh giá tác động; nhân rộng sang tỉnh miền núi khác |

---

## 8. Rủi ro & Giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| **Dịch sai tiếng dân tộc** gây hiểu lầm nguy hiểm | Bắt buộc **người bản ngữ review** trước khi phát chính thức; không tự động 100%. Prompt LLM cấm đổi số liệu/mức độ. |
| **Báo động giả (false alarm)** làm giảm lòng tin | Ngưỡng cấu hình + đo POD/FAR/CSI qua `benchmark.py`; hiệu chỉnh liên tục bằng dữ liệu thực. |
| **Vùng lõm sóng** không nhận cảnh báo | Ưu tiên kênh loa phát thanh; phối hợp trưởng bản. |
| **Phụ thuộc API free tier** (giới hạn lượt gọi) | Cache dữ liệu + fallback nguồn thứ hai (OpenWeatherMap). |
| **Thiếu bản dịch/audio một thời điểm** | Backend & frontend suy giảm mềm: hiển thị bản Tiếng Việt / số liệu thay vì lỗi. |

---

## 9. Đáp ứng yêu cầu tối thiểu của đề bài

| Yêu cầu | Đáp ứng |
|---|---|
| Demo dự báo 3–7 ngày cho ≥3 địa điểm | **12 xã** thuộc 3 huyện × nhiều ngày — `GET /api/forecast/{commune_id}` |
| Dự báo chi tiết dưới cấp tỉnh | Đơn vị **xã/cụm xã** + downscaling theo độ cao thực từng xã |
| Cơ chế cảnh báo tự động theo ngưỡng | `domain/hazard_rules.py` + `config/settings.py: THRESHOLDS`, 8 nhóm hiểm họa 3 mức |
| Bản tin AI + hướng dẫn hành động | `POST /api/pipeline/run` → bản tin vi/thai/hmong + audio + khuyến cáo |
| Cán bộ kiểm tra/phê duyệt | Vòng đời alert + `POST /alerts/{id}/approve\|reject` (X-Officer-Id) |
| Phân phối đa kênh có theo dõi | `POST /alerts/{id}/dispatch` (SMS/Zalo/loa mô phỏng) + bảng `dispatches` |
| Theo dõi phản hồi, cập nhật trạng thái | `feedback` (received/safe/need_help) + `dashboard/overview` |
| Giao diện đơn giản cho người không đọc được bản tin | Thang màu 4 cấp + biểu tượng + pictogram hành động + audio |
| Architecture document + 1-page deck | Tài liệu này + `docs/deck-1page.html` |
