"""Benchmark suite — scores the rule engine against labelled historical scenarios."""
from backend.application.benchmark_data import BENCHMARK_SCENARIOS, TARGET_HAZARDS
from backend.domain.hazard_rules import evaluate_hazards
from backend.shared import alert_levels

_SEP = "-" * 105


def run_evaluation_benchmark() -> None:
    print("=" * 72)
    print("   BỘ ĐÁNH GIÁ HIỆU NĂNG THUẬT TOÁN DỰ BÁO THIÊN TAI (BENCHMARK SUITE)")
    print("=" * 72 + "\n")

    metrics = {hazard: {"TP": 0, "FP": 0, "TN": 0, "FN": 0} for hazard in TARGET_HAZARDS}
    print(f"Bắt đầu chạy thử {len(BENCHMARK_SCENARIOS)} kịch bản thời tiết lịch sử...")
    print(_SEP)

    for case in BENCHMARK_SCENARIOS:
        print(f"Kịch bản #{case['id']}: {case['name']}")
        predicted = {a.hazard: a.level for a in evaluate_hazards(case["weather_data"], case["landslide_risk_factor"])}
        actual = case["ground_truth"]
        print(f"  > Thực tế xảy ra (Ground Truth) : {dict(actual)}")
        print(f"  > Thuật toán dự đoán (Predict)  : {predicted}")

        for hazard in TARGET_HAZARDS:
            _tally(metrics[hazard], predicted.get(hazard), actual.get(hazard))
        print()

    _print_report(metrics)


def _tally(cell: dict, predicted_level, actual_level) -> None:
    predicted_warn = predicted_level in alert_levels.WARNING_LEVELS
    actual_warn = actual_level in alert_levels.WARNING_LEVELS
    if predicted_warn and actual_warn:
        cell["TP"] += 1
    elif predicted_warn:
        cell["FP"] += 1
    elif actual_warn:
        cell["FN"] += 1
    else:
        cell["TN"] += 1


def _skill_scores(tp: int, fp: int, fn: int) -> tuple:
    pod = (tp / (tp + fn) * 100) if (tp + fn) else 100.0
    far = (fp / (tp + fp) * 100) if (tp + fp) else 0.0
    csi = (tp / (tp + fp + fn) * 100) if (tp + fp + fn) else 100.0
    return pod, far, csi


def _print_report(metrics: dict) -> None:
    print(_SEP)
    print("TỔNG HỢP KẾT QUẢ ĐÁNH GIÁ HIỆU NĂNG THUẬT TOÁN DỰ BÁO (BENCHMARK REPORT)")
    print(_SEP)
    header = (
        f"{'Loại hiểm họa':<25} | {'TP':<4} | {'FP':<4} | {'FN':<4} | {'TN':<4} | "
        f"{'Độ nhạy POD (%)':<17} | {'Tỷ lệ giả FAR (%)':<17} | {'CSI Score (%)':<15}"
    )
    print(header)
    print(_SEP)

    total = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
    for hazard in TARGET_HAZARDS:
        m = metrics[hazard]
        for k in total:
            total[k] += m[k]
        pod, far, csi = _skill_scores(m["TP"], m["FP"], m["FN"])
        print(
            f"{hazard:<25} | {m['TP']:<4} | {m['FP']:<4} | {m['FN']:<4} | {m['TN']:<4} | "
            f"{pod:<17.1f} | {far:<17.1f} | {csi:<15.1f}"
        )
    print(_SEP)

    grand = total["TP"] + total["FP"] + total["FN"] + total["TN"]
    accuracy = (total["TP"] + total["TN"]) / grand * 100 if grand else 100.0
    pod, far, csi = _skill_scores(total["TP"], total["FP"], total["FN"])
    print("CHỈ SỐ ĐÁNH GIÁ CHẤT LƯỢNG TỔNG HỢP TÍCH LŨY (TẤT CẢ HIỂM HỌA):")
    print(f" * Độ chính xác tổng thể (Accuracy)      : {accuracy:.1f} %")
    print(f" * Xác suất phát hiện thiên tai (POD)     : {pod:.1f} %")
    print(f" * Tỷ lệ báo động giả (FAR)             : {far:.1f} %")
    print(f" * Chỉ số thành công cốt lõi (CSI)        : {csi:.1f} %")
    print("=" * 72)


if __name__ == "__main__":
    run_evaluation_benchmark()
