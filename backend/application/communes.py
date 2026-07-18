"""
Sinh danh sách xã/cụm xã đại diện cho mỗi huyện (đơn vị dự báo vi mô).

Đây là dữ liệu ĐẠI DIỆN cho demo: tên xã là xã có thật của Điện Biên, còn toạ
độ/độ cao được suy ra quanh tâm huyện. Cấu trúc trùng khớp `domain.Commune` nên
dễ thay bằng dữ liệu đo đạc thật sau này (chỉ cần thay file communes.json).
"""
from typing import List

from backend.config import settings
from backend.infrastructure import json_store

# Tên xã có thật theo huyện + slug id. Lấy COMMUNES_PER_DISTRICT xã đầu mỗi huyện.
_COMMUNE_NAMES = {
    "muong_nhe": [("sin_thau", "Xã Sín Thầu"), ("chung_chai", "Xã Chung Chải"),
                  ("nam_ke", "Xã Nậm Kè"), ("muong_toong", "Xã Mường Toong")],
    "muong_cha": [("na_sang", "Xã Na Sang"), ("muong_muon", "Xã Mường Mươn"),
                  ("hua_ngai", "Xã Hừa Ngài"), ("sa_tong", "Xã Sá Tổng")],
    "tuan_giao": [("quai_nua", "Xã Quài Nưa"), ("chieng_sinh", "Xã Chiềng Sinh"),
                  ("toa_tinh", "Xã Tỏa Tình"), ("pu_nhung", "Xã Pú Nhung")],
}

# Lệch toạ độ (độ) và biến thiên độ cao/hệ số rủi ro quanh tâm huyện — cố định để tái lập.
_LAT_OFFSET = [0.08, -0.08, 0.05, -0.07]
_LON_OFFSET = [0.09, 0.06, -0.10, -0.07]
_ELEV_DELTA = [120, -80, 210, -50]
_RISK_DELTA = [0.10, -0.05, 0.15, 0.0]


def generate_communes() -> List[dict]:
    """Sinh communes từ locations.json (3 huyện). Không ghi file."""
    districts = json_store.load_locations()
    communes: List[dict] = []
    for district in districts:
        names = _COMMUNE_NAMES.get(district["id"], [])[: settings.COMMUNES_PER_DISTRICT]
        for i, (slug, name) in enumerate(names):
            communes.append({
                "id": slug,
                "name": name,
                "district_id": district["id"],
                "district_name": district["name"],
                "lat": round(district["lat"] + _LAT_OFFSET[i], 4),
                "lon": round(district["lon"] + _LON_OFFSET[i], 4),
                "real_elevation": max(300, int(district["real_elevation"] + _ELEV_DELTA[i])),
                "landslide_risk_factor": round(max(0.8, district["landslide_risk_factor"] + _RISK_DELTA[i]), 2),
            })
    return communes


def generate_and_save() -> List[dict]:
    """Sinh và ghi data/communes.json. Trả về danh sách xã."""
    communes = generate_communes()
    json_store.write_json(settings.COMMUNES_FILE, communes)
    return communes


if __name__ == "__main__":  # self-check: đủ xã, khóa id duy nhất, tọa độ hợp lệ
    out = generate_communes()
    assert len(out) == len(_COMMUNE_NAMES) * settings.COMMUNES_PER_DISTRICT, "sai số lượng xã"
    assert len({c["id"] for c in out}) == len(out), "id xã trùng"
    assert all(20 < c["lat"] < 24 and 101 < c["lon"] < 104 for c in out), "toạ độ ngoài Điện Biên"
    print(f"OK — sinh {len(out)} xã cho {len(_COMMUNE_NAMES)} huyện")
