"""
notification_service.py
------------------------
Doc ban tin canh bao da dich (alert.json), tra cuu nguoi dan trong vung
anh huong tu SQL Server (dienbien_weather) va GUI EMAIL THAT toi ho theo
thu tu uu tien: muc canh bao (Red > Orange > Yellow) -> do tuoi (nguoi
gia/tre nho truoc).

CHE DO TEST: chi xu ly toi da 5 nguoi dung co id tu 1 den 5 (TOP 5) de
tranh gui nham vao 45 email gia con lai trong bang du lieu mau.

Chay: python notification_service.py
"""
import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import pyodbc
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# ---------------------------------------------------------------------------
# Cau hinh
# ---------------------------------------------------------------------------
SQL_CONNECTION_STRING = os.getenv("SQL_CONNECTION_STRING", "").strip('"').strip("'")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com").strip('"').strip("'")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "").strip('"').strip("'")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "").replace(" ", "").strip('"').strip("'")

TEST_MODE = True
MAX_TEST_USERS = 5

ALERT_LEVEL_PRIORITY = {"Red": 3, "Orange": 2, "Yellow": 1, "Green": 0}
DISTRICT_PREFIXES = ["Huyện ", "Thành phố ", "Thị xã "]
ETHNIC_LANG_MAP = {
    "kinh": "vi",
    "thái": "thai",
    "thai": "thai",
    "hmong": "hmong",
    "h'mong": "hmong",
    "mông": "hmong",
}

CANDIDATE_ALERT_PATHS = [
    os.path.join(BASE_DIR, "output", "alert.json"),
    os.path.join(PROJECT_ROOT, "translation_agent", "output", "alert.json"),
    os.path.join(BASE_DIR, "alert.json"),
]


# ---------------------------------------------------------------------------
# Tien ich
# ---------------------------------------------------------------------------
def normalize_district(location: str) -> str:
    """'Huyện Mường Nhé' -> 'Mường Nhé' de khop voi cot huyen trong DB."""
    name = location.strip()
    for prefix in DISTRICT_PREFIXES:
        if name.startswith(prefix):
            return name[len(prefix):].strip()
    return name


def resolve_language(dan_toc: Optional[str]) -> str:
    key = (dan_toc or "").strip().lower()
    return ETHNIC_LANG_MAP.get(key, "vi")


def load_alerts() -> List[Dict[str, Any]]:
    import json

    for path in CANDIDATE_ALERT_PATHS:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                alerts = json.load(f)
            print(f"[OK] Da doc {len(alerts)} ban tin canh bao tu {path}")
            return alerts
    raise FileNotFoundError(
        "Khong tim thay alert.json. Da tim tai: " + ", ".join(CANDIDATE_ALERT_PATHS)
    )


def sort_alerts_by_priority(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        alerts,
        key=lambda a: ALERT_LEVEL_PRIORITY.get(a.get("highest_alert_level", "Green"), 0),
        reverse=True,
    )


def sort_recipients_by_priority(recipients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def priority_group(person: Dict[str, Any]) -> int:
        age = person.get("tuoi") or 0
        return 0 if (age >= 60 or age <= 12) else 1

    return sorted(recipients, key=priority_group)


# ---------------------------------------------------------------------------
# Gui email that
# ---------------------------------------------------------------------------
def send_email_alert(to_email: str, subject: str, body: str) -> bool:
    """Gui email canh bao that qua SMTP. Tra ve True/False, khong bao gio raise."""
    if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD]):
        print("[LOI] Thieu cau hinh SMTP trong .env (SMTP_SERVER/SMTP_PORT/SENDER_EMAIL/SENDER_PASSWORD).")
        return False

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        print(f"    -> [SUCCESS] Da gui email toi {to_email}")
        return True
    except Exception as exc:
        print(f"    -> [FAILED] Gui email toi {to_email} loi: {exc}")
        return False


# ---------------------------------------------------------------------------
# Truy van DB
# ---------------------------------------------------------------------------
def fetch_recipients(cur, huyen: str) -> List[Dict[str, Any]]:
    id_limit = MAX_TEST_USERS if TEST_MODE else 999999999
    cur.execute(
        f"""
        SELECT TOP ({MAX_TEST_USERS}) id, ho_ten, tuoi, dan_toc, email
        FROM nguoi_dan
        WHERE huyen = ? AND nhan_canh_bao = 1 AND id <= ?
        ORDER BY id
        """,
        huyen, id_limit,
    )
    columns = [c[0] for c in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def already_notified(cur, nguoi_dan_id: int, warning_id: str) -> bool:
    cur.execute(
        "SELECT 1 FROM notification_logs WHERE nguoi_dan_id = ? AND warning_id = ?",
        nguoi_dan_id, warning_id,
    )
    return cur.fetchone() is not None


def log_notification(cur, nguoi_dan_id: int, warning_id: str, status: str) -> None:
    cur.execute(
        """
        INSERT INTO notification_logs (nguoi_dan_id, warning_id, send_time, status)
        VALUES (?, ?, ?, ?)
        """,
        nguoi_dan_id, warning_id, datetime.now(), status,
    )


# ---------------------------------------------------------------------------
# Pipeline chinh
# ---------------------------------------------------------------------------
def build_subject(alert: Dict[str, Any]) -> str:
    level = alert.get("highest_alert_level", "Yellow")
    return f"[CANH BAO {level.upper()}] {alert.get('location')} - {alert.get('date')}"


def process_alert(cur, alert: Dict[str, Any]) -> None:
    location = alert.get("location", "")
    date = alert.get("date", "")
    huyen = normalize_district(location)
    warning_id = f"{location}_{date}"
    messages = alert.get("messages", {})
    subject = build_subject(alert)

    print(f"\n=== Cảnh báo: {location} ({huyen}) - {date} - Mức {alert.get('highest_alert_level')} ===")

    recipients = fetch_recipients(cur, huyen)
    if not recipients:
        print(f"    (Không có người dân đăng ký cảnh báo tại huyện '{huyen}')")
        return

    recipients = sort_recipients_by_priority(recipients)

    for person in recipients:
        nguoi_dan_id = person["id"]
        email = person.get("email")

        if already_notified(cur, nguoi_dan_id, warning_id):
            print(f"    - Bỏ qua {person.get('ho_ten')} (id={nguoi_dan_id}): đã gửi cảnh báo này trước đó.")
            continue

        if not email:
            print(f"    - Bỏ qua {person.get('ho_ten')} (id={nguoi_dan_id}): không có email.")
            log_notification(cur, nguoi_dan_id, warning_id, "FAILED")
            continue

        lang = resolve_language(person.get("dan_toc"))
        body = messages.get(lang) or messages.get("vi", "")

        print(f"    - Gửi tới {person.get('ho_ten')} (id={nguoi_dan_id}, tuổi={person.get('tuoi')}, "
              f"dân tộc={person.get('dan_toc')}, ngôn ngữ={lang}) -> {email}")

        success = send_email_alert(email, subject, body)
        status = "SUCCESS" if success else "FAILED"
        log_notification(cur, nguoi_dan_id, warning_id, status)


def run() -> None:
    if not SQL_CONNECTION_STRING:
        print("[LOI] Thieu bien SQL_CONNECTION_STRING trong .env")
        return

    alerts = load_alerts()
    alerts = sort_alerts_by_priority(alerts)

    conn = None
    try:
        conn = pyodbc.connect(SQL_CONNECTION_STRING)
        cur = conn.cursor()

        for alert in alerts:
            process_alert(cur, alert)
            conn.commit()

        print("\n[XONG] Hoàn tất xử lý gửi thông báo.")
    except pyodbc.Error as exc:
        print(f"[LOI] Lỗi kết nối/truy vấn SQL Server: {exc}")
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    run()
