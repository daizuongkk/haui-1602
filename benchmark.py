import json
from datetime import datetime
from rule_engine import evaluate_hazards

# ==============================================================================
# BỘ DỮ LIỆU ĐỐI CHỨNG LỊCH SỬ (BENCHMARK DATASET - GROUND TRUTH)
# ==============================================================================
BENCHMARK_SCENARIOS = [
    {
        "id": 1,
        "name": "Mường Nhé - Mưa lớn dồn dập, đất sườn dốc đã no nước",
        "location_id": "muong_nhe",
        "landslide_risk_factor": 1.2,
        "weather_data": {
            "max_precipitation_1h": 45.0,
            "sum_precipitation_24h": 160.0,
            "avg_soil_moisture_27_to_81cm": 0.43,
            "avg_soil_moisture_0_to_1cm": 0.45,
            "sum_evapo_24h": 0.2,
            "max_cape": 1200,
            "max_wind_gust": 35.0,
            "max_wind_speed": 12.0,
            "min_freezing_height": 5200.0,
            "min_temp_adjusted": 21.0,
            "min_soil_temp_adjusted": 20.0,
            "min_visibility": 800.0,
            "max_pressure_drop_3h": 1.0,
            "avg_humidity": 98.0,
            "min_humidity": 90.0,
            "min_cloud": 95.0
        },
        "ground_truth": {
            "Lũ quét & Sạt lở": "Red",
            "Mưa lớn & Ngập úng": "Red"
        }
    },
    {
        "id": 2,
        "name": "Tủa Chùa - Rét đậm hại đêm đông quang mây, ẩm cao",
        "location_id": "tua_chua",
        "landslide_risk_factor": 1.0,
        "weather_data": {
            "max_precipitation_1h": 0.0,
            "sum_precipitation_24h": 0.0,
            "avg_soil_moisture_27_to_81cm": 0.25,
            "avg_soil_moisture_0_to_1cm": 0.22,
            "sum_evapo_24h": 0.8,
            "max_cape": 0,
            "max_wind_gust": 12.0,
            "max_wind_speed": 4.0,
            "min_freezing_height": 1800.0,
            "min_temp_adjusted": 3.2,
            "min_soil_temp_adjusted": -0.8,
            "min_visibility": 8000.0,
            "max_pressure_drop_3h": 0.5,
            "avg_humidity": 92.0,
            "min_humidity": 70.0,
            "min_cloud": 5.0
        },
        "ground_truth": {
            "Sương muối & Băng giá": "Red",
            "Rét đậm, rét hại": "Orange"
        }
    },
    {
        "id": 3,
        "name": "Mường Chả - Sương mù đặc biệt dày đặc trên đèo dốc buổi sáng",
        "location_id": "muong_cha",
        "landslide_risk_factor": 1.1,
        "weather_data": {
            "max_precipitation_1h": 0.0,
            "sum_precipitation_24h": 0.0,
            "avg_soil_moisture_27_to_81cm": 0.28,
            "avg_soil_moisture_0_to_1cm": 0.26,
            "sum_evapo_24h": 1.1,
            "max_cape": 200,
            "max_wind_gust": 10.0,
            "max_wind_speed": 3.0,
            "min_freezing_height": 4800.0,
            "min_temp_adjusted": 16.5,
            "min_soil_temp_adjusted": 16.0,
            "min_visibility": 120.0,
            "max_pressure_drop_3h": 0.2,
            "avg_humidity": 99.0,
            "min_humidity": 85.0,
            "min_cloud": 90.0
        },
        "ground_truth": {
            "Sương mù dày đặc": "Red"
        }
    },
    {
        "id": 4,
        "name": "Tuần Giáo - Giông lốc xoáy mùa hè, mây đối lưu phát triển mạnh",
        "location_id": "tuan_giao",
        "landslide_risk_factor": 1.0,
        "weather_data": {
            "max_precipitation_1h": 18.0,
            "sum_precipitation_24h": 32.0,
            "avg_soil_moisture_27_to_81cm": 0.29,
            "avg_soil_moisture_0_to_1cm": 0.31,
            "sum_evapo_24h": 2.5,
            "max_cape": 3100,
            "max_wind_gust": 85.0,
            "max_wind_speed": 22.0,
            "min_freezing_height": 4900.0,
            "min_temp_adjusted": 24.0,
            "min_soil_temp_adjusted": 23.0,
            "min_visibility": 2500.0,
            "max_pressure_drop_3h": 3.8,
            "avg_humidity": 82.0,
            "min_humidity": 55.0,
            "min_cloud": 60.0
        },
        "ground_truth": {
            "Dông, lốc, sét": "Red"
        }
    },
    {
        "id": 5,
        "name": "Mường Nhé - Mưa đá cục bộ chiều hè",
        "location_id": "muong_nhe",
        "landslide_risk_factor": 1.2,
        "weather_data": {
            "max_precipitation_1h": 25.0,
            "sum_precipitation_24h": 40.0,
            "avg_soil_moisture_27_to_81cm": 0.32,
            "avg_soil_moisture_0_to_1cm": 0.33,
            "sum_evapo_24h": 2.1,
            "max_cape": 2800,
            "max_wind_gust": 65.0,
            "max_wind_speed": 18.0,
            "min_freezing_height": 3400.0,
            "min_temp_adjusted": 22.0,
            "min_soil_temp_adjusted": 21.0,
            "min_visibility": 1500.0,
            "max_pressure_drop_3h": 2.5,
            "avg_humidity": 88.0,
            "min_humidity": 60.0,
            "min_cloud": 75.0
        },
        "ground_truth": {
            "Mưa đá": "Red",
            "Dông, lốc, sét": "Orange"
        }
    },
    {
        "id": 6,
        "name": "Mường Chả - Hanh khô kéo dài, nguy cơ cháy rừng cực độ",
        "location_id": "muong_cha",
        "landslide_risk_factor": 1.1,
        "weather_data": {
            "max_precipitation_1h": 0.0,
            "sum_precipitation_24h": 0.0,
            "avg_soil_moisture_27_to_81cm": 0.18,
            "avg_soil_moisture_0_to_1cm": 0.08,
            "sum_evapo_24h": 3.8,
            "max_cape": 150,
            "max_wind_gust": 25.0,
            "max_wind_speed": 18.0,
            "min_freezing_height": 5500.0,
            "max_temp_adjusted": 38.5,
            "min_temp_adjusted": 27.0,
            "min_soil_temp_adjusted": 26.0,
            "min_visibility": 9000.0,
            "max_pressure_drop_3h": 0.4,
            "avg_humidity": 50.0,
            "min_humidity": 32.0,
            "min_cloud": 5.0
        },
        "ground_truth": {
            "Cháy rừng": "Red"
        }
    },
    {
        "id": 7,
        "name": "Tuần Giáo - Ngày hè nắng ấm, thời tiết bình thường",
        "location_id": "tuan_giao",
        "landslide_risk_factor": 1.0,
        "weather_data": {
            "max_precipitation_1h": 0.0,
            "sum_precipitation_24h": 0.0,
            "avg_soil_moisture_27_to_81cm": 0.30,
            "avg_soil_moisture_0_to_1cm": 0.28,
            "sum_evapo_24h": 2.2,
            "max_cape": 300,
            "max_wind_gust": 15.0,
            "max_wind_speed": 6.0,
            "min_freezing_height": 5400.0,
            "max_temp_adjusted": 32.0,
            "min_temp_adjusted": 22.0,
            "min_soil_temp_adjusted": 21.0,
            "min_visibility": 10000.0,
            "max_pressure_drop_3h": 0.3,
            "avg_humidity": 70.0,
            "min_humidity": 50.0,
            "min_cloud": 40.0
        },
        "ground_truth": {}
    },
    {
        "id": 8,
        "name": "Mường Nhé - Mưa vừa rải rác nhưng đất còn khô (Báo động giả)",
        "location_id": "muong_nhe",
        "landslide_risk_factor": 1.2,
        "weather_data": {
            "max_precipitation_1h": 5.0,
            "sum_precipitation_24h": 25.0,
            "avg_soil_moisture_27_to_81cm": 0.22,
            "avg_soil_moisture_0_to_1cm": 0.20,
            "sum_evapo_24h": 1.2,
            "max_cape": 400,
            "max_wind_gust": 18.0,
            "max_wind_speed": 7.0,
            "min_freezing_height": 5200.0,
            "min_temp_adjusted": 23.0,
            "min_soil_temp_adjusted": 22.0,
            "min_visibility": 6000.0,
            "max_pressure_drop_3h": 0.5,
            "avg_humidity": 85.0,
            "min_humidity": 65.0,
            "min_cloud": 80.0
        },
        "ground_truth": {}
    },
    {
        "id": 9,
        "name": "Tủa Chùa - Đêm đông lạnh kèm mưa phùn ẩm ướt (Không sương muối)",
        "location_id": "tua_chua",
        "landslide_risk_factor": 1.0,
        "weather_data": {
            "max_precipitation_1h": 0.5,
            "sum_precipitation_24h": 3.0,
            "avg_soil_moisture_27_to_81cm": 0.32,
            "avg_soil_moisture_0_to_1cm": 0.35,
            "sum_evapo_24h": 0.3,
            "max_cape": 0,
            "max_wind_gust": 15.0,
            "max_wind_speed": 5.0,
            "min_freezing_height": 2200.0,
            "min_temp_adjusted": 7.5,
            "min_soil_temp_adjusted": 5.0,
            "min_visibility": 2000.0,
            "max_pressure_drop_3h": 0.4,
            "avg_humidity": 96.0,
            "min_humidity": 85.0,
            "min_cloud": 98.0
        },
        "ground_truth": {
            "Rét đậm, rét hại": "Yellow"
        }
    },
    {
        "id": 10,
        "name": "Tuần Giáo - Mưa dông trung bình buổi chiều",
        "location_id": "tuan_giao",
        "landslide_risk_factor": 1.0,
        "weather_data": {
            "max_precipitation_1h": 12.0,
            "sum_precipitation_24h": 22.0,
            "avg_soil_moisture_27_to_81cm": 0.31,
            "avg_soil_moisture_0_to_1cm": 0.34,
            "sum_evapo_24h": 1.5,
            "max_cape": 950,
            "max_wind_gust": 38.0,
            "max_wind_speed": 10.0,
            "min_freezing_height": 5100.0,
            "min_temp_adjusted": 24.5,
            "min_soil_temp_adjusted": 23.5,
            "min_visibility": 4000.0,
            "max_pressure_drop_3h": 1.1,
            "avg_humidity": 88.0,
            "min_humidity": 65.0,
            "min_cloud": 70.0
        },
        "ground_truth": {
            "Dông, lốc, sét": "Yellow"
        }
    }
]

TARGET_HAZARDS = [
    "Lũ quét & Sạt lở",
    "Sương muối & Băng giá",
    "Sương mù dày đặc",
    "Dông, lốc, sét",
    "Mưa đá",
    "Cháy rừng",
    "Mưa lớn & Ngập úng",
    "Rét đậm, rét hại"
]

def run_evaluation_benchmark():
    print("========================================================================")
    print("   BỘ ĐÁNH GIÁ HIỆU NĂNG THUẬT TOÁN DỰ BÁO THIÊN TAI (BENCHMARK SUITE)   ")
    print("========================================================================\n")
    
    # Khởi tạo Confusion Matrix cho từng hiểm họa
    metrics = {hazard: {"TP": 0, "FP": 0, "TN": 0, "FN": 0} for hazard in TARGET_HAZARDS}
    
    print(f"Bắt đầu chạy thử {len(BENCHMARK_SCENARIOS)} kịch bản thời tiết lịch sử...")
    print("-" * 105)
    
    for case in BENCHMARK_SCENARIOS:
        print(f"Kịch bản #{case['id']}: {case['name']}")
        
        # Nhập các quy tắc từ rule_engine.py để tính toán
        # Đầu ra của evaluate_hazards là một danh sách các bộ (Tên, Mức độ, Mô tả)
        raw_alerts = evaluate_hazards(case["weather_data"], case["landslide_risk_factor"])
        
        # Chuyển đổi về dạng dictionary để dễ đối chiếu
        predicted_alerts = {alert[0]: alert[1] for alert in raw_alerts}
        actual_alerts = case["ground_truth"]
        
        print(f"  > Thực tế xảy ra (Ground Truth) : {dict(actual_alerts)}")
        print(f"  > Thuật toán dự đoán (Predict)  : {predicted_alerts}")
        
        for hazard in TARGET_HAZARDS:
            pred_level = predicted_alerts.get(hazard)
            actual_level = actual_alerts.get(hazard)
            
            # Cảnh báo kích hoạt khi đạt mức Cam (Orange) hoặc Đỏ (Red)
            is_pred_warn = pred_level in ["Orange", "Red"]
            is_actual_warn = actual_level in ["Orange", "Red"]
            
            if is_pred_warn and is_actual_warn:
                metrics[hazard]["TP"] += 1
            elif is_pred_warn and not is_actual_warn:
                metrics[hazard]["FP"] += 1
            elif not is_pred_warn and is_actual_warn:
                metrics[hazard]["FN"] += 1
            else:
                metrics[hazard]["TN"] += 1
                
        print()
        
    print("-" * 105)
    print("TỔNG HỢP KẾT QUẢ ĐÁNH GIÁ HIỆU NĂNG THUẬT TOÁN DỰ BÁO (BENCHMARK REPORT)")
    print("-" * 105)
    print(f"{'Loại hiểm họa':<25} | {'TP':<4} | {'FP':<4} | {'FN':<4} | {'TN':<4} | {'Độ nhạy POD (%)':<17} | {'Tỷ lệ giả FAR (%)':<17} | {'CSI Score (%)':<15}")
    print("-" * 105)
    
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_tn = 0
    
    for hazard in TARGET_HAZARDS:
        m = metrics[hazard]
        tp, fp, fn, tn = m["TP"], m["FP"], m["FN"], m["TN"]
        
        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_tn += tn
        
        pod = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 100.0
        far = (fp / (tp + fp) * 100) if (tp + fp) > 0 else 0.0
        csi = (tp / (tp + fp + fn) * 100) if (tp + fp + fn) > 0 else 100.0
        
        print(f"{hazard:<25} | {tp:<4} | {fp:<4} | {fn:<4} | {tn:<4} | {pod:<17.1f} | {far:<17.1f} | {csi:<15.1f}")
        
    print("-" * 105)
    
    overall_accuracy = ((total_tp + total_tn) / (total_tp + total_fp + total_fn + total_tn)) * 100
    overall_pod = (total_tp / (total_tp + total_fn)) * 100 if (total_tp + total_fn) > 0 else 100.0
    overall_far = (total_fp / (total_tp + total_fp)) * 100 if (total_tp + total_fp) > 0 else 0.0
    overall_csi = (total_tp / (total_tp + total_fp + total_fn)) * 100 if (total_tp + total_fp + total_fn) > 0 else 100.0
    
    print("CHỈ SỐ ĐÁNH GIÁ CHẤT LƯỢNG TỔNG HỢP TÍCH LŨY (TẤT CẢ HIỂM HỌA):")
    print(f" * Độ chính xác tổng thể (Accuracy)      : {overall_accuracy:.1f} %")
    print(f" * Xác suất phát hiện thiên tai (POD)     : {overall_pod:.1f} %")
    print(f" * Tỷ lệ báo động giả (FAR)             : {overall_far:.1f} %")
    print(f" * Chỉ số thành công cốt lõi (CSI)        : {overall_csi:.1f} %")
    print("========================================================================")

if __name__ == "__main__":
    run_evaluation_benchmark()
