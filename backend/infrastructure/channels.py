"""
Adapter kênh phân phối — MÔ PHỎNG (implements ports.MessageChannel).

Không gửi tin thật: chỉ trả trạng thái 'sent_sim' để lớp trên ghi log/trạng thái.
Muốn gửi thật: thay các lớp này bằng adapter gọi Zalo OA API / SMS brandname,
giữ nguyên interface `send(payload) -> DispatchResult`.
"""
from backend.infrastructure.ports import DispatchResult


class _SimulatedChannel:
    name = "base"

    def send(self, payload: dict) -> DispatchResult:  # noqa: ARG002 - mô phỏng, không dùng payload
        return DispatchResult(status="sent_sim")


class SimulatedSms(_SimulatedChannel):
    name = "sms"


class SimulatedZalo(_SimulatedChannel):
    name = "zalo"


class SimulatedLoudspeaker(_SimulatedChannel):
    name = "loudspeaker"


def default_channels() -> dict:
    """map tên kênh → adapter mô phỏng."""
    return {c.name: c for c in (SimulatedSms(), SimulatedZalo(), SimulatedLoudspeaker())}
