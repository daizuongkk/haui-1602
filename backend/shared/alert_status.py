"""
Trạng thái vòng đời của một cảnh báo — nguồn chân lý duy nhất.

Luồng: pending_approval → approved → distributed → closed
                       ↘ rejected
"""
PENDING = "pending_approval"
APPROVED = "approved"
REJECTED = "rejected"
DISTRIBUTED = "distributed"
CLOSED = "closed"

ALL = (PENDING, APPROVED, REJECTED, DISTRIBUTED, CLOSED)

LABELS = {
    PENDING: "Chờ phê duyệt",
    APPROVED: "Đã duyệt",
    REJECTED: "Từ chối",
    DISTRIBUTED: "Đã phát",
    CLOSED: "Đã đóng",
}

# Trạng thái được phép chuyển sang từ mỗi trạng thái (dùng để chặn thao tác sai luồng).
TRANSITIONS = {
    PENDING: {APPROVED, REJECTED},
    APPROVED: {DISTRIBUTED, CLOSED, REJECTED},
    DISTRIBUTED: {CLOSED, DISTRIBUTED},  # phát thêm kênh vẫn ở distributed
    REJECTED: {PENDING},
    CLOSED: set(),
}


def can_transition(current: str, target: str) -> bool:
    return target in TRANSITIONS.get(current, set())


# Phản hồi của người dân.
FEEDBACK_KINDS = ("received", "safe", "need_help")
FEEDBACK_LABELS = {"received": "Đã nhận", "safe": "An toàn", "need_help": "Cần hỗ trợ"}
