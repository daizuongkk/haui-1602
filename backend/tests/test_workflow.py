"""
Tests cho lớp vòng đời cảnh báo (DB) — chạy offline, không mạng/LLM.

Dùng SQLite in-memory + fake MessageChannel để kiểm luồng
upsert → duyệt/từ chối → phân phối → phản hồi và các guard chuyển trạng thái.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.application import alert_service, dispatch_service, feedback_service
from backend.application.communes import generate_communes
from backend.infrastructure.db.models import Base, Officer
from backend.infrastructure.ports import DispatchResult
from backend.shared import alert_status


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    db.add(Officer(id="off1", name="Cán bộ 1", role="test"))
    db.flush()
    yield db
    db.close()


def _sample_record(commune_id="nam_ke", date="20/07/2026", level="Orange", messages=None):
    return {
        "commune_id": commune_id, "commune_name": "Xã Nậm Kè",
        "district_id": "muong_nhe", "district_name": "Huyện Mường Nhé",
        "latitude": 22.2, "longitude": 102.4, "elevation": 900, "date": date,
        "highest_alert_level": level,
        "weather_summary": {"total_rain": 60}, "hazards": [{"hazard": "Lũ quét", "level": level, "description": "x"}],
        "messages": messages or {"vi": "Cảnh báo"}, "audio": {}, "has_translation": True,
    }


class FakeChannel:
    def __init__(self, name, ok=True):
        self.name = name
        self._ok = ok

    def send(self, payload):
        return DispatchResult(status="sent_sim") if self._ok else DispatchResult("failed", "boom")


def test_upsert_creates_then_updates(session):
    a, created, _ = alert_service.upsert_alert(session, _sample_record())
    assert created and a.status == alert_status.PENDING
    # Cùng (commune, date) → cập nhật, không tạo mới.
    _, created2, _ = alert_service.upsert_alert(session, _sample_record(level="Red"))
    assert not created2
    assert len(alert_service.list_alerts(session)) == 1
    assert alert_service.list_alerts(session)[0].highest_alert_level == "Red"


def test_rerun_resets_approved_to_pending_on_change(session):
    a, _, _ = alert_service.upsert_alert(session, _sample_record())
    alert_service.approve(session, a.id, "off1")
    assert a.status == alert_status.APPROVED
    # Chạy lại đổi nội dung → phải duyệt lại.
    alert_service.upsert_alert(session, _sample_record(level="Red"))
    assert a.status == alert_status.PENDING and a.approved_by is None


def test_dispatch_requires_approval(session):
    a, _, _ = alert_service.upsert_alert(session, _sample_record())
    with pytest.raises(alert_service.AlertError):
        dispatch_service.dispatch(session, a.id, ["sms"], "off1",
                                  adapters={"sms": FakeChannel("sms")})


def test_full_flow_dispatch_and_feedback(session):
    a, _, _ = alert_service.upsert_alert(session, _sample_record())
    alert_service.approve(session, a.id, "off1")
    result = dispatch_service.dispatch(
        session, a.id, ["sms", "zalo"], "off1",
        adapters={"sms": FakeChannel("sms"), "zalo": FakeChannel("zalo")},
    )
    assert a.status == alert_status.DISTRIBUTED
    assert len(result["dispatches"]) == 2
    assert all(d.status == "sent_sim" for d in result["dispatches"])

    feedback_service.record_feedback(session, a.id, "need_help", note="kẹt")
    feedback_service.record_feedback(session, a.id, "safe")
    counts = feedback_service.counts_for_alert(session, a.id)
    assert counts["need_help"] == 1 and counts["safe"] == 1
    assert feedback_service.total_need_help(session) == 1


def test_reject_then_rerun_allows_pending_again(session):
    a, _, _ = alert_service.upsert_alert(session, _sample_record())
    alert_service.reject(session, a.id, "off1", "sai số liệu")
    assert a.status == alert_status.REJECTED
    with pytest.raises(alert_service.AlertError):  # không được phát khi đã từ chối
        dispatch_service.dispatch(session, a.id, ["sms"], "off1", adapters={"sms": FakeChannel("sms")})


def test_bad_feedback_kind_rejected(session):
    a, _, _ = alert_service.upsert_alert(session, _sample_record())
    with pytest.raises(alert_service.AlertError):
        feedback_service.record_feedback(session, a.id, "invalid_kind")


def test_generate_communes_shape():
    communes = generate_communes()
    assert len(communes) == 12
    assert {c["district_id"] for c in communes} == {"muong_nhe", "muong_cha", "tuan_giao"}
    assert all(c["real_elevation"] >= 300 for c in communes)
