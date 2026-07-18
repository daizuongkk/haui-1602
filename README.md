<h1 align="center">🌦️ Hệ thống AI Cảnh báo & Dự báo Thời tiết Vi mô — Điện Biên</h1>

<p align="center">
  <b>"Đúng người – Đúng lúc – Đúng ngôn ngữ"</b><br/>
  Dự báo thiên tai đến cấp huyện/cụm bản · Cảnh báo tự động · Bản tin đa ngôn ngữ (Việt · Thái · H'Mông) · Hiểu được kể cả khi không đọc được chữ
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white">
  <img alt="Next.js" src="https://img.shields.io/badge/Next.js%2015-React%2019-000000?logo=nextdotjs&logoColor=white">
  <img alt="AI" src="https://img.shields.io/badge/AI-Downscaling·RuleEngine·LLM·TTS-8A2BE2">
  <img alt="Challenge" src="https://img.shields.io/badge/Vietnam-AI%20Innovation%20Challenge-red">
</p>

---

Ở vùng cao Điện Biên, thời tiết cực đoan (lũ quét, sạt lở, rét hại, sương muối, dông lốc) xảy ra **nhanh và cục bộ**, nhưng dự báo hiện chỉ ở **cấp tỉnh** — đến chậm, khó hiểu với đồng bào dân tộc, và bỏ sót nhiều bản làng. Dự án này biến dữ liệu thời tiết thô thành **cảnh báo hành động cụ thể, đa ngôn ngữ, truyền bằng màu sắc – biểu tượng – giọng nói**, để **ai cũng hiểu được mức nguy hiểm và việc cần làm**.

## 🎯 Vấn đề

- Dự báo cấp tỉnh **không phản ánh vi khí hậu từng xã** (chênh lệch độ cao lớn → nguy cơ khác nhau).
- Bản tin dùng **thuật ngữ khí tượng** khó chuyển thành hành động.
- **Rào cản ngôn ngữ & chữ viết**: nhiều đồng bào Thái, H'Mông không đọc thạo/không đọc được chữ.
- **Vùng lõm sóng** không nhận được cảnh báo qua Internet.

## 💡 Giải pháp — Pipeline AI 4 lớp

```
Open-Meteo API
   └─(1) Hạ độ phân giải theo địa hình  → dự báo cấp xã
        └─(2) Rule Engine 7 hiểm họa × 4 mức (ngưỡng hiệu chỉnh)
             └─(3) LLM sinh bản tin + dịch Việt→Thái→H'Mông + TTS giọng nói
                  └─(4) Phân phối: Dashboard · SMS · Zalo OA · Loa phát thanh xã
```

**Điểm nổi bật**
- 🏔️ **Dự báo vi mô** cấp huyện/cụm bản, hiệu chỉnh nhiệt độ theo độ cao thực từng xã.
- 🈯 **Cảnh báo đa ngôn ngữ dân tộc** (Thái Tai Dam/Tai Don, H'Mông RPA) + **giọng nói**, có ràng buộc chống bịa số liệu.
- 🎨 **Giao diện không cần đọc chữ**: thang 4 màu (🟢🟡🟠🔴) + biểu tượng hiểm họa + pictogram hành động.
- 🔄 **Quy trình khép kín có kiểm duyệt**: mỗi cảnh báo đi qua vòng đời *chờ duyệt → duyệt → phát → đóng* (SQLite), có ghi nhận phản hồi từ cơ sở — không chỉ sinh bản tin mà quản lý cả việc phê duyệt & phân phối.
- 📊 **Đo lường được**: bộ benchmark báo cáo POD/FAR/CSI trên kịch bản lịch sử.

## 🖼️ Demo

| Màn hình Người dân | Dashboard Ban Chỉ huy PCTT |
|:---:|:---:|
| ![Người dân](docs/screenshots/resident.png) | ![Dashboard](docs/screenshots/dashboard.png) |

## 🧠 AI được sử dụng

| Kỹ thuật | Vai trò |
|---|---|
| **Statistical downscaling** | Hiệu chỉnh nhiệt độ theo địa hình (lapse rate) → dự báo sát từng xã |
| **Rule-based hazard model** | 7 nhóm hiểm họa × 4 mức; điểm rủi ro sạt lở là công thức tổng hợp |
| **LLM (sinh + dịch)** | Bản tin tiếng Việt chuẩn → dịch ngôn ngữ ít tài nguyên (Thái, H'Mông), chống ảo giác |
| **Text-to-Speech** | Giọng nói cho người không đọc chữ & loa phát thanh |

## 🚀 Chạy thử

Yêu cầu: **Python 3.11+**, **Node 18+**. Chạy các lệnh Python **từ thư mục gốc**.

```bash
# 1) Backend API
pip install -r backend/requirements.txt
uvicorn backend.presentation.api.app:app --reload      # http://localhost:8000

# 2) Frontend
cd frontend && npm install && npm run dev              # http://localhost:5173
```

Mở **http://localhost:5173** → tab **Người dân** và **Ban Chỉ huy PCTT**.

```bash
# (Tuỳ chọn) Sinh lại dữ liệu & đánh giá thuật toán
python -m backend.presentation.cli          # dự báo → data/active_alerts.json
python -m backend.presentation.cli seed     # khởi tạo SQLite + cán bộ + cảnh báo demo (offline, không cần LLM)
python -m backend.presentation.benchmark    # POD / FAR / CSI
python -m pytest backend/tests              # kiểm thử
```

> Bước dịch đa ngôn ngữ cần `GEMINI_API_KEY` trong file `.env` ở thư mục gốc. Repo đã kèm sẵn kết quả (`data/output/`) và lệnh `seed` nạp 21 bản tin thực vào SQLite, nên toàn bộ quy trình (kể cả duyệt & phân phối trên dashboard) chạy được ngay không cần mạng/API key.

## ☁️ Deploy (Frontend Vercel · Backend Render)

Kiến trúc: **frontend Next.js trên Vercel**, **backend FastAPI trên Render**. Frontend gọi backend qua Next.js rewrites (`BACKEND_URL`) nên trình duyệt chỉ dùng đường dẫn tương đối — không vướng CORS.

**1) Backend → Render** (đã có sẵn [`render.yaml`](render.yaml)):
- Render Dashboard → **New → Blueprint** → chọn repo này → Apply.
- (Tuỳ chọn) đặt `GEMINI_API_KEY` để bật dịch Thái/H'Mông. Không có key backend vẫn tự lấy dữ liệu Open-Meteo lúc khởi động và sinh cảnh báo tiếng Việt.
- Ghi lại URL, ví dụ `https://dienbien-weather-api.onrender.com`.

**2) Frontend → Vercel:**
- Vercel → **Add New → Project** → import repo → đặt **Root Directory = `frontend`** (Next.js tự nhận diện).
- Thêm biến môi trường **`BACKEND_URL`** = URL Render ở bước 1 → **Deploy**.

> Render gói free ngủ sau ~15 phút không dùng → lần gọi đầu chờ ~50s (cold start). Trạng thái SQLite bền trong lúc instance chạy; muốn bền vĩnh viễn thì gắn Persistent Disk (trả phí). Xem `.env.example` và `frontend/.env.example` để biết các biến.

## 📁 Cấu trúc dự án

```
backend/     # Toàn bộ mã server-side (Clean Architecture)
  config/  shared/  domain/  infrastructure/  application/  presentation/  tests/
frontend/    # Giao diện Next.js 15 (App Router) + React 19 + TypeScript + Tailwind (app / components / lib)
data/        # Dữ liệu chạy + sản phẩm sinh ra (JSON + audio) + SQLite lifecycle (app.db)
docs/        # Hồ sơ dự thi, kiến trúc, deck, ảnh demo
```

Kiến trúc phân lớp, phụ thuộc hướng vào trong (`presentation → application → domain`; `infrastructure` hiện thực các port) — dễ kiểm thử, dễ mở rộng.

## 🗺️ Lộ trình

**Pilot** (1 huyện, kết nối Đài KTTV) → **Hiệu chỉnh** (dữ liệu thực, mở rộng tỉnh) → **Đa ngôn ngữ chính thức** (chuẩn hoá từ vựng với giáo viên song ngữ) → **Loa xã & SMS** (truyền thanh thông minh, cell broadcast).

## 🔌 API (Swagger / OpenAPI)

API do FastAPI sinh tài liệu tự động. Khởi động backend rồi mở:

- **Swagger UI** → http://localhost:8000/docs (bấm *Try it out* để gọi thử)
- **ReDoc** → http://localhost:8000/redoc · **OpenAPI JSON** → `/openapi.json` ([bản kèm sẵn](docs/openapi.json))

Chi tiết đầy đủ (endpoint, schema, ví dụ cURL): **[docs/API.md](docs/API.md)**.

## 📄 Tài liệu

- 📌 **[Hồ sơ dự thi đầy đủ](docs/BAI-DU-THI.md)** — vấn đề, giải pháp, tác động, đối chiếu tiêu chí chấm.
- 🏗️ **[Kiến trúc chi tiết](docs/architecture.md)** — nguồn dữ liệu, mô hình xử lý, API, rủi ro.
- 🔌 **[Tài liệu API](docs/API.md)** — Swagger/OpenAPI, endpoint, schema, ví dụ.
- 🖥️ **[Deck 1 trang](docs/deck-1page.html)** — tóm tắt trình bày.

## 👥 Đội ngũ

Mô hình 6 vai trò: Trưởng nhóm/UX · Data · Forecast/ML · AI/NLP · Backend/DevOps · QA/Frontend. *(Chi tiết trong [hồ sơ dự thi](docs/BAI-DU-THI.md#9-đội-ngũ).)*

---

<p align="center"><i>AI phục vụ những người cần nó nhất. 🇻🇳</i></p>
