import json
import sqlite3
import os
import sys
from datetime import datetime

# Đảm bảo import đúng cấu hình
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Kết nối đường dẫn trực tiếp với thư mục data/ của dự án lớn
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "voai_database.db"))
PENDING_ALERTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "pending_alerts.json"))
ACTIVE_ALERTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "active_alerts.json"))

def init_alerts_log():
    """ Khởi tạo bảng nhật ký duyệt phát tin cảnh báo """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id TEXT,
            hazard_type TEXT,
            level TEXT,
            expert_status TEXT,
            text_vi TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_alert_to_db(location_id, hazard_type, level, status, text_vi):
    """ Ghi nhận kết quả duyệt của chuyên gia (ko chấp thuận / chấp thuận) vào DB """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts_log (
            location_id, hazard_type, level, expert_status, text_vi, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        location_id,
        hazard_type,
        level,
        status,
        text_vi,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def main():
    print("=== VOAI EXPERT VALIDATION CHECKPOINT START ===")
    init_alerts_log()
    
    if not os.path.exists(PENDING_ALERTS_PATH):
        print(f"❌ Không tìm thấy tệp {PENDING_ALERTS_PATH}. Vui lòng chạy main.py trước.")
        return
        
    with open(PENDING_ALERTS_PATH, "r", encoding="utf-8") as f:
        pending_alerts = json.load(f)
        
    if not pending_alerts:
        print("💡 Không có cảnh báo nào đang chờ duyệt.")
        return
        
    print(f"📋 Tìm thấy {len(pending_alerts)} khu vực cảnh báo chờ phê duyệt.\n")
    approved_alerts = []
    
    # Kiểm tra xem có tham số duyệt nhanh tự động không
    auto_approve = len(sys.argv) > 1 and sys.argv[1] == "--approve-all"
    
    for loc_alert in pending_alerts:
        loc_id = loc_alert["location_id"]
        loc_name = loc_alert["location"]
        date_str = loc_alert["date"]
        alerts = loc_alert["alerts"]
        
        if not alerts:
            print(f"👉 Địa điểm {loc_name} không có nguy cơ thiên tai. Tự động bỏ qua.")
            continue
            
        print(f"\n==================================================")
        print(f"📍 ĐỊA ĐIỂM: {loc_name} | NGÀY: {date_str}")
        print(f"--------------------------------------------------")
        for idx, alert in enumerate(alerts):
            print(f"  {idx + 1}. [{alert['level']}] {alert['hazard']}: {alert['description']}")
        print(f"==================================================")
        
        # Hỏi ý kiến Chuyên gia
        decision = "y"
        if not auto_approve:
            decision = input("Phê duyệt các cảnh báo này? (y: Chấp thuận / n: Không chấp thuận / q: Thoát): ").strip().lower()
            
        if decision == 'q':
            print("Thoát chương trình.")
            break
        elif decision == 'y' or auto_approve:
            print(f"✔ Đã chấp thuận cảnh báo tại {loc_name}. Đang ghi nhận...")
            
            loc_alert["expert_status"] = "Approved"
            
            # Ghi nhận trạng thái duyệt cho từng cảnh báo
            for alert in alerts:
                vi_text = f"Cảnh báo {alert['hazard']} mức {alert['level']} tại {loc_name}. {alert['description']}"
                alert["text_vi"] = vi_text
                
                # Lưu lịch sử duyệt thành công vào DB
                log_alert_to_db(
                    location_id=loc_id,
                    hazard_type=alert["hazard"],
                    level=alert["level"],
                    status="Approved",
                    text_vi=vi_text
                )
                
            approved_alerts.append(loc_alert)
            
        else:
            print(f"❌ Không chấp thuận (Từ chối cảnh báo tại {loc_name}). Ghi nhận báo động giả.")
            loc_alert["expert_status"] = "Rejected"
            
            for alert in alerts:
                vi_text = f"Cảnh báo {alert['hazard']} mức {alert['level']} tại {loc_name}. {alert['description']}"
                # Lưu lịch sử bị từ chối vào DB
                log_alert_to_db(
                    location_id=loc_id,
                    hazard_type=alert["hazard"],
                    level=alert["level"],
                    status="Rejected",
                    text_vi=vi_text
                )
                
    # Ghi nhận danh sách đã duyệt phát hành ra file JSON sạch
    with open(ACTIVE_ALERTS_PATH, "w", encoding="utf-8") as f:
        json.dump(approved_alerts, f, indent=2, ensure_ascii=False)
        
    print(f"\n✔ Đã xuất danh sách cảnh báo được phê duyệt ra file JSON: {ACTIVE_ALERTS_PATH}")
    print("=== VOAI EXPERT VALIDATION CHECKPOINT FINISHED ===")

if __name__ == "__main__":
    main()
