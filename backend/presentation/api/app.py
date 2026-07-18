"""FastAPI application factory and ASGI entry point (`backend.presentation.api.app:app`)."""
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

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
    def startup_event():
        import os
        import sys
        from pathlib import Path
        
        # 1. Khởi tạo DB & communes
        print("\n⚡ [STARTUP] Khởi tạo cơ sở dữ liệu và dữ liệu xã/cụm xã...")
        try:
            from backend.application import seed
            init_db()
            with session_scope() as session:
                seed.seed_officers(session)
            seed.ensure_communes()
            print("⚡ [STARTUP] Khởi tạo DB & communes thành công.")
        except Exception as db_err:
            print(f"❌ [STARTUP] Lỗi khởi tạo DB: {db_err}")

        # 2. Chạy toàn bộ Orchestrator Pipeline trong luồng nền (Asynchronous Background Thread)
        print("⚡ [STARTUP] Đang kích hoạt luồng nền để cập nhật thời tiết, dịch thuật & sinh giọng đọc...")
        import threading
        
        def run_pipeline_bg():
            try:
                from backend.application.run_pipeline import run_pipeline
                
                # Kiểm tra xem có API Key cho dịch thuật hay không
                api_key = os.getenv("GEMINI_API_KEY")
                do_translate = bool(api_key)
                
                with session_scope() as session:
                    # Do_tts=True để sinh giọng đọc loa thông báo cho người dân
                    stats = run_pipeline(session, do_translate=do_translate, do_tts=True)
                    
                print(f"\n⚡ [BACKGROUND-PIPELINE] Hoàn thành cập nhật thời tiết và dịch thuật! Kết quả: {stats}")
            except Exception as e:
                print(f"\n❌ [BACKGROUND-PIPELINE] Lỗi khi chạy cập nhật thời tiết: {e}")

        # Khởi chạy luồng nền không chặn uvicorn
        threading.Thread(target=run_pipeline_bg, daemon=True).start()

    return app


app = create_app()
