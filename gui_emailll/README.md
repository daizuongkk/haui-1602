# Hệ thống AI Cảnh báo & Dự báo Thời tiết Vi mô — Điện Biên

> **"Đúng người – Đúng lúc – Đúng ngôn ngữ"**
> Dự báo chi tiết cấp huyện · Cảnh báo thiên tai tự động theo ngưỡng · Bản tin đa ngôn ngữ (Việt · Thái · H'Mông) · Giao diện trực quan cho người dân.

Tài liệu kiến trúc đầy đủ: [`docs/architecture.md`](docs/architecture.md) · Deck 1 trang: [`docs/deck-1page.html`](docs/deck-1page.html).

## Cấu trúc dự án

```
backend/     ← Toàn bộ mã server-side (Python, Clean Architecture)
frontend/    ← Giao diện React + Vite
data/        ← Dữ liệu chạy + sản phẩm sinh ra (JSON + audio)
docs/        ← Tài liệu kiến trúc, deck, spec
main.py, benchmark.py   ← Shim tương thích, gọi vào backend/
```

**`backend/` — các lớp theo Clean Architecture** (phụ thuộc hướng vào trong:
`presentation → application → domain`; `infrastructure` hiện thực các port):

| Lớp | Trách nhiệm |
|---|---|
| `backend/config/` | Cấu hình tập trung: ngưỡng (`THRESHOLDS`), đường dẫn, model, hằng số |
| `backend/shared/` | Từ vựng dùng chung (thang mức cảnh báo) |
| `backend/domain/` | Nghiệp vụ thuần, không I/O: downscaling, rule engine, tổng hợp ngày, models |
| `backend/infrastructure/` | Adapter I/O: Open-Meteo, Gemini, gTTS, đọc/ghi JSON, audio catalog, ports |
| `backend/application/` | Use case điều phối: forecast, dịch thuật, TTS, hợp nhất, phân phối |
| `backend/presentation/` | Điểm vào: `cli`, `benchmark`, `translation_cli`, `tts_cli`, `api/` (FastAPI) |
| `backend/tests/` | Kiểm thử domain + use case (không cần mạng) |

**`data/`** — hợp đồng dữ liệu dùng chung giữa pipeline, agent dịch và API:
`locations.json`, `active_alerts.json`, `output/alert.json`, `output/audio/<huyện>/<ngày>/<lang>.mp3`.

## Chạy demo

Yêu cầu: **Python 3.11+**, **Node 18+**. Chạy các lệnh Python **từ thư mục gốc**.

### 1. Sinh dữ liệu dự báo & cảnh báo
```bash
pip install -r backend/requirements.txt
python -m backend.presentation.cli          # → data/active_alerts.json  (hoặc: python main.py)
```

### 2. Sinh bản tin đa ngôn ngữ & audio (tùy chọn — repo đã có sẵn kết quả)
```bash
# cần GEMINI_API_KEY trong file .env ở thư mục gốc cho bước dịch
python -m backend.presentation.translation_cli   # → data/output/alert.json
python -m backend.presentation.tts_cli           # → data/output/audio/<huyện>/<ngày>/<lang>.mp3
```

### 3. Backend API
```bash
uvicorn backend.presentation.api.app:app --reload   # http://localhost:8000
python -m pytest backend/tests                       # kiểm thử domain + use case
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173  (proxy /api & /audio → :8000)
```

Mở **http://localhost:5173** → tab **Người dân** (thang màu + icon + audio) và **Ban Chỉ huy PCTT** (bản đồ + danh sách + chi tiết + mô phỏng gửi cảnh báo).

## API chính

| Endpoint | Mô tả |
|---|---|
| `GET /api/summary` | Mức cảnh báo cao nhất theo huyện + đếm KPI |
| `GET /api/forecast/{location_id}` | Dự báo 3–7 ngày (`muong_nhe`, `muong_cha`, `tuan_giao`) |
| `GET /api/alerts/active` | Các ngày có cảnh báo (số liệu + bản tin + audio) |
| `POST /api/alerts/broadcast` | Mô phỏng gửi SMS / Zalo OA / loa phát thanh (không gửi thật) |

Các lệnh cũ (`python main.py`, `python benchmark.py`, `uvicorn backend.main:app`) vẫn chạy được nhờ shim tương thích ở thư mục gốc / `backend/main.py`.
