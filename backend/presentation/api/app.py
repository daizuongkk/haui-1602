"""FastAPI application factory and ASGI entry point (`backend.presentation.api.app:app`)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.infrastructure.db.session import init_db, session_scope
from backend.presentation.api.routes import router

API_DESCRIPTION = """
API của **Hệ thống AI Cảnh báo & Dự báo Thời tiết Vi mô — Điện Biên**.

Cung cấp dữ liệu dự báo/cảnh báo thiên tai cấp huyện, bản tin đa ngôn ngữ (Việt · Thái · H'Mông),
và mô phỏng phân phối đa kênh cho giao diện người dân + dashboard chỉ huy.

### Khái niệm chính
- **Mức cảnh báo (4 cấp):** `Green` (Bình thường) · `Yellow` (Chú ý) · `Orange` (Nguy hiểm) · `Red` (Cực kỳ nguy hiểm).
- **Khoá dữ liệu:** mỗi bản ghi định danh bằng `(location_id, date)` với `date` dạng `dd/mm/yyyy`.
- **Audio:** các URL `/audio/...` trỏ tới file mp3 tĩnh (giọng đọc bản tin theo ngôn ngữ).

### Ghi chú
- API **chỉ đọc**; endpoint phân phối **chỉ mô phỏng**, không gửi SMS/Zalo/loa thật.
- Tài liệu tương tác: **Swagger UI** tại `/docs`, **ReDoc** tại `/redoc`, đặc tả JSON tại `/openapi.json`.
"""

TAGS_METADATA = [
    {"name": "Địa điểm", "description": "Danh mục xã/cụm xã được giám sát và toạ độ."},
    {"name": "Cán bộ", "description": "Danh sách cán bộ (xác thực nhẹ qua header X-Officer-Id)."},
    {"name": "Cảnh báo", "description": "Tổng quan, danh sách và chi tiết cảnh báo theo vòng đời."},
    {"name": "Dự báo", "description": "Chuỗi dự báo 3–7 ngày theo xã."},
    {"name": "Phê duyệt", "description": "Cán bộ duyệt/từ chối/cập nhật trạng thái cảnh báo."},
    {"name": "Phân phối", "description": "Phát cảnh báo qua SMS / Zalo OA / loa (mô phỏng, có lưu log)."},
    {"name": "Phản hồi", "description": "Người dân gửi phản hồi; theo dõi tình hình tiếp nhận."},
    {"name": "Pipeline", "description": "Kích hoạt chạy phân tích dự báo → sinh cảnh báo."},
    {"name": "Dashboard", "description": "Chỉ số điều hành tổng hợp."},
    {"name": "Hệ thống", "description": "Kiểm tra tình trạng dịch vụ."},
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="Điện Biên Weather Alert API",
        version="1.0.0",
        description=API_DESCRIPTION,
        openapi_tags=TAGS_METADATA,
        contact={"name": "Đội dự thi — Vietnam AI Innovation Challenge"},
        license_info={"name": "MIT"},
        swagger_ui_parameters={"docExpansion": "list", "displayRequestDuration": True},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.API_CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.AUDIO_ROOT.exists():
        app.mount("/audio", StaticFiles(directory=str(settings.AUDIO_ROOT)), name="audio")

    app.include_router(router)

    @app.on_event("startup")
    def _bootstrap() -> None:
        # Tạo bảng + seed cán bộ + đảm bảo có communes.json. Idempotent.
        from backend.application import seed
        init_db()
        with session_scope() as session:
            seed.seed_officers(session)
        seed.ensure_communes()

    return app


app = create_app()
