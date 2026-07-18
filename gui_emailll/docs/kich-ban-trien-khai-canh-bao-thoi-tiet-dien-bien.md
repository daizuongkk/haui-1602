# KỊCH BẢN TRIỂN KHAI CHI TIẾT
## Hệ thống AI Cảnh báo & Dự báo Thời tiết Vi mô cho Điện Biên
### "Đúng người – Đúng lúc – Đúng ngôn ngữ"

---

## 0. TÓM TẮT GIẢI PHÁP (dùng cho slide 1-page deck)

**Bài toán:** Điện Biên có địa hình chia cắt mạnh, thời tiết cực đoan xảy ra nhanh (sương mù, lũ quét, sương muối) nhưng dự báo hiện chỉ ở cấp tỉnh, đến chậm, khó hiểu với đồng bào dân tộc thiểu số.

**Giải pháp:** Một pipeline AI 4 lớp:
1. **Thu thập & hạ độ phân giải (downscaling)** dữ liệu thời tiết cấp tỉnh → cấp xã/cụm bản, kết hợp dữ liệu lịch sử thiên tai để hiệu chỉnh.
2. **Mô hình phát hiện rủi ro + sinh cảnh báo tự động** bằng ngưỡng (rule-based) kết hợp LLM để soạn bản tin dễ hiểu.
3. **Dịch đa ngôn ngữ** (Việt → Thái, Mông) bằng LLM + kiểm duyệt người bản ngữ.
4. **Phân phối đa kênh**: App/Zalo OA cho cán bộ xã, SMS cho hộ dân, loa phát thanh cho bản không sóng.

**Giao diện:** Thang cảnh báo 4 màu (Xanh–Vàng–Cam–Đỏ) + icon, không phụ thuộc chữ viết.

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LỚP NGUỒN DỮ LIỆU                             │
│  Open-Meteo API │ OpenWeatherMap API │ Đài KTTV Điện Biên (thủ công/  │
│  file Excel-CSV) │ Dữ liệu lịch sử thiên tai (Ban Chỉ huy PCTT)       │
└───────────────────────────────┬────────────────────────────────────-┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LỚP THU THẬP & CHUẨN HÓA (ETL)                     │
│  - Cron job gọi API mỗi 1-3h                                          │
│  - Chuẩn hóa toạ độ theo lưới xã/cụm bản (geo-mapping)                │
│  - Lưu vào Data Warehouse (Postgres + PostGIS / TimescaleDB)          │
└───────────────────────────────┬────────────────────────────────────-┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                LỚP XỬ LÝ & MÔ HÌNH (Forecast Engine)                  │
│  - Downscaling thống kê (nội suy địa hình + hiệu chỉnh bias theo      │
│    trạm KTTV thực tế)                                                 │
│  - Rule Engine phát hiện ngưỡng nguy hiểm (mưa lớn, sương muối...)    │
│  - LLM (Claude) sinh bản tin cảnh báo ngôn ngữ tự nhiên + dịch        │
└───────────────────────────────┬────────────────────────────────────-┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LỚP PHÂN PHỐI (Distribution Layer)                 │
│  Zalo OA (cán bộ xã/dân có smartphone) │ SMS Gateway (dân không có    │
│  app) │ API loa phát thanh xã (text-to-speech tiếng dân tộc) │        │
│  Web Dashboard cho Ban Chỉ huy PCTT tỉnh                              │
└───────────────────────────────┬────────────────────────────────────-┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│              LỚP NGƯỜI DÙNG CUỐI (giao diện đơn giản hoá)             │
│  App/Zalo: bản đồ màu cảnh báo, icon, giọng nói │ SMS: text ngắn có   │
│  emoji-code │ Loa: audio 30 giây, lặp lại 3 lần                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. PHÂN VAI TRÒ (ROLES) TRONG ĐỘI TRIỂN KHAI — TEAM 6 NGƯỜI

8 mảng việc gốc được gộp lại thành 6 role để vừa khớp quy mô nhóm, vừa tránh nghẽn ở các mắt xích lõi của pipeline (Data → Forecast → AI/NLP giữ độc lập, không gộp).

| # | Role | Gánh vác từ mảng việc gốc | Trách nhiệm chính |
|---|------|------------------------------|---------------------|
| 1 | **Trưởng nhóm / Product Owner kiêm UX** | Product Owner + Frontend/UX Designer | Định nghĩa yêu cầu, làm việc với "khách hàng giả định" (Ban PCTT tỉnh), chốt scope demo, viết deck; thiết kế wireframe thang màu/icon/bản đồ (không cần code) |
| 2 | **#2 Data Engineer** | Data Engineer (giữ nguyên) | Kết nối API thời tiết, xây ETL, thiết kế database, geo-mapping xã/bản |
| 3 | **Forecast/ML Engineer** | Forecast Engineer (giữ nguyên) | Xây mô hình downscaling, rule engine ngưỡng cảnh báo, hiệu chỉnh với dữ liệu lịch sử |
| 4 | **AI/NLP Engineer (LLM)** | AI/NLP Engineer (giữ nguyên) | Prompt engineering sinh bản tin, pipeline dịch đa ngôn ngữ, TTS |
| 5 | **Backend/Integration kiêm DevOps** | Backend/Integration + DevOps | API service, tích hợp Zalo OA, SMS gateway, webhook loa phát thanh, deploy hạ tầng, giám sát |
| 6 | **QA / Field Validation kiêm Frontend dev** | QA + phần thực thi code giao diện | Code giao diện theo wireframe của #1 (dashboard, screen demo), đồng thời là người test độc lập ngưỡng cảnh báo và độ dễ hiểu của giao diện |

**Vì sao chia thế này:**
- Data – Forecast – AI/NLP là 3 mắt xích lõi của pipeline (thu thập → xử lý → sinh ngôn ngữ), mỗi mắt xích có input/output rõ ràng nên giữ độc lập, tránh 1 người phải context-switch giữa xử lý số liệu và prompt engineering.
- UX gộp với Trưởng nhóm thay vì gộp với Backend, vì thiết kế thang màu/icon là quyết định sản phẩm (bám sát người dùng cuối), không phải kỹ thuật thuần túy.
- QA tách riêng khỏi người viết rule engine, để tránh việc "người viết ngưỡng cảnh báo tự kiểm tra ngưỡng của chính mình" — dễ bỏ sót lỗi. QA được ghép với việc code giao diện vì đây là người cần "nhìn bằng con mắt người dùng".

---

## 3. CHI TIẾT TASK THEO TỪNG ROLE (theo giai đoạn)

### GIAI ĐOẠN 0 — Chuẩn bị & Thu thập yêu cầu (Ngày 1)

**#1 Trưởng nhóm/PO kiêm UX**
- [ ] Xác định 3-5 khu vực demo cụ thể (ví dụ: TP Điện Biên Phủ, huyện Mường Nhé — vùng lũ quét, huyện Tủa Chùa — vùng sương muối cao nguyên đá)
- [ ] Liệt kê danh sách hiểm họa ưu tiên: mưa lớn/lũ quét, sương muối, dông lốc, sương mù dày
- [ ] Xác định nhóm người dùng đích: (a) cán bộ xã/bản, (b) hộ nông dân, (c) người đi đường/vận tải
- [ ] Soạn khung 1-page deck (mục lục, thông điệp chính)
- [ ] Nghiên cứu chuẩn màu cảnh báo quốc tế (Xanh/Vàng/Cam/Đỏ) và icon thời tiết phổ thông dễ hiểu không cần biết chữ
- [ ] Phác thảo wireframe: màn hình bản đồ, thẻ cảnh báo, tin nhắn SMS mẫu (giao cho #6 code lại ở Giai đoạn 4)

**#2 Data Engineer**
- [ ] Đăng ký API key Open-Meteo (free) và OpenWeatherMap (free tier)
- [ ] Thu thập ranh giới hành chính Điện Biên (GeoJSON cấp huyện/xã) từ nguồn mở (GADM, OpenStreetMap)
- [ ] Liệt kê danh sách trạm khí tượng thủ công của Đài KTTV Điện Biên (nếu không có API, ghi nhận là "manual data feed" trong kiến trúc)

**#3 Forecast/ML Engineer**
- [ ] Nghiên cứu ngưỡng cảnh báo chuẩn của Việt Nam (theo QCVN hoặc văn bản Ban Chỉ đạo TW về PCTT): mưa to (≥50mm/24h), mưa rất to (≥100mm/24h), rét đậm (<15°C), rét hại (<13°C), sương muối (nhiệt độ mặt đất ~0°C kèm độ ẩm cao trời quang)
- [ ] Thu thập dữ liệu lịch sử thiên tai Điện Biên (nếu có sẵn công khai) để đối chiếu hiệu chỉnh sau này

**#4 AI/NLP Engineer**
- [ ] Khảo sát khả năng dịch Việt→Thái/Mông của các mô hình sẵn có (LLM đa ngôn ngữ, hoặc từ điển chuyên gia bản ngữ để review)
- [ ] Lên danh sách template bản tin cảnh báo mẫu (cấu trúc: Mức độ – Hiện tượng – Thời gian – Hành động cần làm)

---

### GIAI ĐOẠN 1 — Xây dựng lớp dữ liệu (Ngày 2)

**#2 Data Engineer** (task chính)
- [ ] Viết script ETL gọi Open-Meteo API theo tọa độ trung tâm của từng cụm xã (chọn ~10-15 điểm đại diện phủ các vùng địa hình khác nhau: lòng chảo, cao nguyên đá, vùng biên giới)
- [ ] Chuẩn hóa dữ liệu trả về: nhiệt độ, lượng mưa (mm/h, mm/24h), độ ẩm, tốc độ gió, tầm nhìn xa (visibility – cho sương mù), điểm sương (dew point – cho sương muối)
- [ ] Thiết kế schema database:
  - `locations` (id, tên xã/cụm bản, huyện, lat, lon, độ cao, đặc điểm địa hình)
  - `weather_raw` (location_id, timestamp, nguồn, các chỉ số thời tiết)
  - `weather_forecast_downscaled` (location_id, ngày, chỉ số dự báo đã hiệu chỉnh)
  - `alert_thresholds` (loại hiểm họa, ngưỡng, mức độ)
  - `alerts_issued` (id, location_id, loại cảnh báo, mức độ, thời điểm, nội dung, kênh đã gửi)
- [ ] Thiết lập cron job (mỗi 3 giờ) đồng bộ dữ liệu mới

**#3 Forecast/ML Engineer**
- [ ] Xây hàm downscaling đơn giản: nội suy dữ liệu lưới thô (~9-11km của Open-Meteo) theo độ cao địa hình (hiệu chỉnh nhiệt độ theo gradient khí quyển ~0.65°C/100m) để ra số liệu sát hơn cho từng xã vùng cao
- [ ] Nếu có dữ liệu trạm KTTV thực tế: tính hệ số hiệu chỉnh (bias correction) giữa dự báo API và số đo thực tế gần nhất

---

### GIAI ĐOẠN 2 — Rule Engine cảnh báo & sinh bản tin AI (Ngày 3)

**#3 Forecast/ML Engineer**
- [ ] Code rule engine dạng bảng ngưỡng có thể cấu hình (không hard-code) — ví dụ:

| Hiểm họa | Chỉ số | Ngưỡng Vàng | Ngưỡng Cam | Ngưỡng Đỏ |
|---|---|---|---|---|
| Mưa lớn/lũ quét | Lượng mưa 24h | 50-100mm | 100-150mm | >150mm |
| Rét/sương muối | Nhiệt độ thấp nhất | 13-15°C | 8-13°C | <8°C hoặc có sương muối |
| Sương mù | Tầm nhìn xa | 500m-1km | 200-500m | <200m |
| Dông lốc | Tốc độ gió giật | 40-60km/h | 60-90km/h | >90km/h |

- [ ] Viết logic quét dữ liệu forecast mỗi lần ETL chạy → so ngưỡng → tạo record cảnh báo nếu vượt

**#4 AI/NLP Engineer**
- [ ] Thiết kế prompt template gọi LLM để sinh bản tin cảnh báo từ dữ liệu structured, ví dụ:
  - Input: `{xã: "Sín Thầu", hiểm_họa: "lũ quét", mức_độ: "Đỏ", thời_gian: "đêm nay đến sáng mai", lượng_mưa_dự_kiến: "180mm"}`
  - Output mong muốn: bản tin ngắn (≤60 từ) gồm: hiện tượng gì, khi nào, hành động cụ thể ("di dời khỏi khu vực ven suối", "không qua ngầm tràn")
- [ ] Xây pipeline dịch: bản tin tiếng Việt chuẩn → dịch sang tiếng Thái/Mông bằng LLM → **bắt buộc có bước review bởi người bản ngữ/cộng tác viên xã trước khi phát chính thức** (ghi rõ trong tài liệu như một quy trình bắt buộc, không tự động hoàn toàn vì rủi ro dịch sai có thể gây hại)
- [ ] Tích hợp Text-to-Speech (TTS) cho bản tin loa phát thanh (ưu tiên tiếng Việt phổ thông trước, tiếng dân tộc là giai đoạn mở rộng)

---

### GIAI ĐOẠN 3 — Phân phối đa kênh (Ngày 3-4)

**#5 Backend/Integration kiêm DevOps**
- [ ] Xây REST API nội bộ: `GET /forecast/{location_id}`, `GET /alerts/active`, `POST /alerts/broadcast`
- [ ] Tích hợp Zalo Official Account API: gửi tin nhắn broadcast tới nhóm cán bộ xã đã theo dõi OA (dùng Zalo OA Notification Message hoặc ZNS - Zalo Notification Service cho tin cảnh báo chính thức)
- [ ] Tích hợp SMS Gateway (mô phỏng trong demo bằng SMS API sandbox hoặc giả lập, vì SMS thật cần hợp đồng viễn thông) — thiết kế format SMS ngắn gọn có mã cảnh báo (VD: `[ĐỎ-LŨ QUÉT] Xã Sín Thầu: Mưa rất to đêm nay. KHÔNG qua suối/ngầm tràn. Alo 113 nếu cần cứu hộ.`)
- [ ] Thiết kế API webhook giả lập cho "hệ thống loa phát thanh xã" — trả về file audio (MP3 từ bước TTS) + text hiển thị, để mô phỏng việc trạm loa xã tải về và phát
- [ ] Song song deploy backend lên môi trường cloud free-tier phù hợp demo (Render/Railway/VPS nhỏ) — không chờ đến cuối mới deploy, để có môi trường thật cho #6 test sớm
- [ ] Thiết lập log & giám sát cơ bản (thời gian phản hồi, lỗi API)

> **Lưu ý timeline riêng cho team 6 người:** vì #5 gánh cả phần tích hợp lẫn deploy, nên bắt đầu song song từ đầu Ngày 3 (không làm tuần tự tích hợp xong mới deploy) để tránh dồn việc vào cuối Giai đoạn 3.

---

### GIAI ĐOẠN 4 — Giao diện người dùng cuối (Ngày 4-5)

**#6 QA/Field Validation kiêm Frontend dev** (thực thi theo wireframe của #1)
- [ ] Xây dashboard web đơn giản (cho Ban PCTT/cán bộ xã):
  - Bản đồ Điện Biên với các điểm/vùng tô màu theo mức cảnh báo hiện tại
  - Click vào từng xã → xem dự báo 3-7 ngày dạng thẻ (card) với icon: ☀️🌧️❄️🌫️
  - Danh sách cảnh báo đang hiệu lực, có nút "Gửi lại cảnh báo"
- [ ] Thiết kế giao diện mô phỏng phía người dân (screen demo trên điện thoại):
  - Thang cảnh báo 4 màu lớn, rõ, không cần đọc chữ vẫn hiểu mức nguy hiểm
  - Icon hành động khuyến nghị (VD: hình người sơ tán, hình cấm qua ngầm tràn)
  - Nút nghe bản tin bằng giọng nói (audio player)
- [ ] Thiết kế mẫu tin nhắn SMS và kịch bản audio loa phát thanh (script demo)

**#1 Trưởng nhóm/PO kiêm UX**
- [ ] Bổ sung wireframe chi tiết nếu #6 cần làm rõ trong lúc code (làm việc song song, không chờ wireframe hoàn chỉnh 100% mới bắt đầu)

> **Lưu ý timeline riêng cho team 6 người:** #6 nên bắt đầu code giao diện ngay khi có wireframe sơ bộ từ #1 (cuối Ngày 3), chạy song song với Giai đoạn 3, để dành đủ thời gian test ở Giai đoạn 5.

---

### GIAI ĐOẠN 5 — Kiểm thử & hoàn thiện demo (Ngày 5-6)

**#6 QA/Field Validation kiêm Frontend dev**
- [ ] Test dự báo 3-7 ngày cho tối thiểu 3 địa điểm khác biệt về địa hình (VD: TP Điện Biên Phủ - lòng chảo thấp, Tủa Chùa - cao nguyên đá dễ sương muối, Mường Nhé - biên giới dễ lũ quét)
- [ ] Test cơ chế cảnh báo: giả lập dữ liệu vượt ngưỡng (inject test data) → xác nhận hệ thống tự sinh bản tin đúng mức độ, đúng kênh
- [ ] Test khả năng "người không biết chữ hiểu được": cho người ngoài nhóm (không giải thích trước) xem giao diện, hỏi họ đoán mức độ nguy hiểm là gì — ghi nhận % hiểu đúng
- [ ] Kiểm tra bản dịch tiếng Thái/Mông với người bản ngữ (nếu có thể tiếp cận) hoặc ít nhất note rõ đây là bước cần continuous review

**#1 Trưởng nhóm/PO kiêm UX**
- [ ] Tổng hợp toàn bộ vào 1-page deck: bài toán → giải pháp → kiến trúc → demo → roadmap
- [ ] Viết Architecture Document đầy đủ (xem mục 5 bên dưới)
- [ ] Chuẩn bị kịch bản trình bày demo (script 5 phút)

---

## 4. LỘ TRÌNH TRIỂN KHAI THỰC TẾ (ROADMAP SAU HACKATHON)

| Giai đoạn | Thời gian | Mục tiêu |
|---|---|---|
| **Pilot** | Tháng 1-3 | Triển khai thử nghiệm tại 1 huyện trọng điểm thiên tai (VD: Mường Nhé), kết nối trực tiếp với Đài KTTV Điện Biên để lấy dữ liệu trạm thực, thiết lập kênh Zalo OA chính thức với 5-10 xã |
| **Mở rộng dữ liệu & hiệu chỉnh** | Tháng 3-6 | Thu thập phản hồi thực tế cảnh báo đúng/sai (false positive/negative), hiệu chỉnh mô hình downscaling bằng dữ liệu quan trắc thực, mở rộng ra toàn bộ các huyện |
| **Đa ngôn ngữ chính thức** | Tháng 4-7 | Hợp tác với cán bộ văn hóa dân tộc/giáo viên song ngữ để xây bộ từ vựng chuẩn cảnh báo thiên tai tiếng Thái, Mông; kiểm định chất lượng dịch |
| **Kết nối hạ tầng loa xã** | Tháng 6-9 | Làm việc với các xã có hệ thống truyền thanh thông minh để tích hợp API tự động phát bản tin |
| **SMS chính thức & nhân rộng toàn tỉnh** | Tháng 9-12 | Ký hợp đồng với nhà mạng viễn thông cho SMS cảnh báo khẩn cấp (cell broadcast nếu khả thi), đánh giá tác động, báo cáo Ban Chỉ đạo PCTT tỉnh để nhân rộng mô hình sang các tỉnh miền núi khác |

---

## 5. NỘI DUNG ARCHITECTURE DOCUMENT (tóm tắt cấu trúc để viết đầy đủ)

1. **Nguồn dữ liệu (Data Sources)**
   - Open-Meteo, OpenWeatherMap: API, tần suất cập nhật, độ phân giải lưới, giới hạn free tier
   - Đài KTTV Điện Biên: hình thức tiếp nhận (thủ công/API nếu có), vai trò hiệu chỉnh bias
   - Dữ liệu lịch sử thiên tai Ban Chỉ huy PCTT: dùng để backtest ngưỡng cảnh báo

2. **Mô hình xử lý (Processing Model)**
   - Downscaling thống kê theo địa hình
   - Rule-based threshold engine (có bảng ngưỡng cấu hình được, không hard-code, để dễ điều chỉnh theo mùa/khu vực)
   - LLM layer: sinh bản tin ngôn ngữ tự nhiên + dịch đa ngữ + TTS
   - Vòng phản hồi (feedback loop): dữ liệu thực tế đúng/sai được ghi nhận để tinh chỉnh ngưỡng theo thời gian

3. **Kênh phân phối (Distribution Channels)**
   - Zalo OA/ZNS: cán bộ xã, người dân có smartphone
   - SMS: hộ dân không dùng app
   - Loa phát thanh xã: audio tự động, khu vực không sóng/không đọc chữ
   - Dashboard web: Ban Chỉ huy PCTT cấp tỉnh/huyện giám sát tổng thể

4. **Lộ trình triển khai (Deployment Roadmap)** — như bảng mục 4

5. **Rủi ro & giảm thiểu**
   - Rủi ro dịch sai ngôn ngữ dân tộc gây hiểu lầm → bắt buộc review người bản ngữ, không phát tự động 100%
   - Rủi ro cảnh báo giả (false alarm) làm giảm lòng tin → cơ chế hiệu chỉnh liên tục bằng dữ liệu thực tế + hiển thị độ tin cậy
   - Rủi ro vùng lõm sóng không nhận được cảnh báo → ưu tiên kênh loa phát thanh, phối hợp trưởng bản
   - Rủi ro phụ thuộc API free tier (giới hạn số lượt gọi) → thiết kế cache + fallback sang nguồn dữ liệu thứ hai

---

## 6. MAPPING VỚI YÊU CẦU TỐI THIỂU CỦA ĐỀ BÀI

| Yêu cầu đề bài | Đáp ứng bởi |
|---|---|
| Demo dự báo 3-7 ngày cho ≥3 địa điểm | Giai đoạn 1 (Data Engineer) + Giai đoạn 5 (QA test 3 địa điểm địa hình khác nhau) |
| Cơ chế cảnh báo tự động theo ngưỡng | Giai đoạn 2 (Forecast Engineer - Rule Engine) |
| Giao diện đơn giản cho người không đọc được bản tin khí tượng | Giai đoạn 4 (UX - thang màu, icon) + Giai đoạn 5 (test độ hiểu) |
| Architecture document + 1-page deck | Giai đoạn 5 (#1 Trưởng nhóm/PO) + mục 5 tài liệu này |

---

*Tài liệu này có thể dùng trực tiếp làm khung phân công công việc trong nhóm và làm nội dung cốt lõi cho Architecture Document nộp bài.*
