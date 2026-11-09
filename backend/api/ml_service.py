import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH_DIRECT = BASE_DIR / 'models' / 'xgboost_water_model.pkl'
PREP_PATH_DIRECT = BASE_DIR / 'models' / 'water_preprocessor.pkl'

MODEL_PATH_ROOT = BASE_DIR.parent / 'xgboost_water_model.pkl'
PREP_PATH_ROOT = BASE_DIR.parent / 'water_preprocessor.pkl'

_model = None
_preprocessor = None

FEATURE_NAMES = [
    'ph',
    'Hardness',
    'Solids',
    'Chloramines',
    'Sulfate',
    'Conductivity',
    'Organic_carbon',
    'Trihalomethanes',
    'Turbidity'
]

# Chuẩn kỹ thuật theo WHO & QCVN 01-1:2018/BYT
METRIC_STANDARDS = {
    'ph': {
        'name': 'Độ pH',
        'unit': 'pH',
        'min_val': 6.5,
        'max_val': 8.5,
        'standard_desc': '6.5 - 8.5 (QCVN / WHO)',
        'description': 'Đo tính axit hoặc kiềm của nước. Giá trị < 6.5 gây ăn mòn kim loại, > 8.5 gây vị đắng và đóng cặn.'
    },
    'Hardness': {
        'name': 'Độ cứng (Hardness)',
        'unit': 'mg/L',
        'min_val': 0,
        'max_val': 300.0,
        'standard_desc': '< 300 mg/L CaCO₃',
        'description': 'Lượng ion Canxi và Magie hòa tan. Nước quá cứng (>300) đóng cặn ấm đun và ảnh hưởng tiêu hóa.'
    },
    'Solids': {
        'name': 'Tổng chất rắn hòa tan (TDS)',
        'unit': 'ppm',
        'min_val': 0,
        'max_val': 1000.0,
        'standard_desc': '< 500 - 1000 ppm',
        'description': 'Tổng khoáng chất, muối và kim loại hòa tan. Mức tối ưu uống < 500 ppm, trên 1000 ppm có vị lạ.'
    },
    'Chloramines': {
        'name': 'Chloramines',
        'unit': 'ppm',
        'min_val': 0,
        'max_val': 4.0,
        'standard_desc': '< 4.0 ppm',
        'description': 'Chất khử trùng kết hợp giữa Clo và Amoniac. Nồng độ quá cao có thể gây kích ứng da, mắt và mùi hôi.'
    },
    'Sulfate': {
        'name': 'Nồng độ Sunfat (Sulfate)',
        'unit': 'mg/L',
        'min_val': 0,
        'max_val': 250.0,
        'standard_desc': '< 250 mg/L',
        'description': 'Hợp chất tự nhiên trong khoáng sản. Nồng độ > 250-400 mg/L có thể gây tác dụng nhuận tràng.'
    },
    'Conductivity': {
        'name': 'Độ dẫn điện (EC)',
        'unit': 'μS/cm',
        'min_val': 0,
        'max_val': 400.0,
        'warning_val': 750.0,
        'standard_desc': '< 400 μS/cm (tối đa 750)',
        'description': 'Đo khả năng truyền dòng điện, tỷ lệ thuận với lượng ion ion hóa trong nước.'
    },
    'Organic_carbon': {
        'name': 'Cacbon hữu cơ (TOC)',
        'unit': 'ppm',
        'min_val': 0,
        'max_val': 4.0,
        'warning_val': 10.0,
        'standard_desc': '< 2.0 - 4.0 ppm',
        'description': 'Chỉ số đo chất hữu cơ phân hủy sinh học trong nước. Mức cao tạo điều kiện cho vi khuẩn phát triển.'
    },
    'Trihalomethanes': {
        'name': 'Trihalomethanes (THMs)',
        'unit': 'μg/L',
        'min_val': 0,
        'max_val': 80.0,
        'standard_desc': '< 80 μg/L',
        'description': 'Phụ phẩm hóa học sinh ra khi Clo phản ứng với chất hữu cơ, là chất có nguy cơ gây hại sức khỏe lâu dài.'
    },
    'Turbidity': {
        'name': 'Độ đục (Turbidity)',
        'unit': 'NTU',
        'min_val': 0,
        'max_val': 5.0,
        'ideal_val': 1.0,
        'standard_desc': '< 5.0 NTU (lý tưởng < 1.0)',
        'description': 'Đo độ trong suốt của nước do các hạt lơ lửng gây ra. Nước đục có nguy cơ nhiễm vi sinh vật cao.'
    }
}

PRESET_SAMPLES = [
    {
        'id': 'safe_sample_high',
        'title': 'Mẫu nước đạt chuẩn an toàn cao (Potable)',
        'desc': 'Mẫu thực tế trong tập dữ liệu: pH 8.85, tỷ lệ an toàn dự đoán 96.5%.',
        'values': {
            'ph': 8.85,
            'Hardness': 188.92,
            'Solids': 32033.33,
            'Chloramines': 13.13,
            'Sulfate': 182.4,
            'Conductivity': 479.79,
            'Organic_carbon': 12.07,
            'Trihalomethanes': 77.67,
            'Turbidity': 4.01
        }
    },
    {
        'id': 'alkaline_safe',
        'title': 'Nước khoáng kiềm an toàn (Potable)',
        'desc': 'Mẫu khoáng kiềm tự nhiên: pH 9.81, độ cứng hài hòa, độ an toàn 96.4%.',
        'values': {
            'ph': 9.81,
            'Hardness': 220.05,
            'Solids': 34132.07,
            'Chloramines': 9.75,
            'Sulfate': 233.87,
            'Conductivity': 367.04,
            'Organic_carbon': 13.5,
            'Trihalomethanes': 62.95,
            'Turbidity': 4.48
        }
    },
    {
        'id': 'tap_water_polluted',
        'title': 'Nước ô nhiễm hữu cơ & Clo (Không đạt)',
        'desc': 'Nước có dư lượng Clo và phụ phẩm THMs cao, pH thấp mang tính axit.',
        'values': {
            'ph': 3.72,
            'Hardness': 129.42,
            'Solids': 18630.06,
            'Chloramines': 6.64,
            'Sulfate': 333.78,
            'Conductivity': 592.89,
            'Organic_carbon': 15.18,
            'Trihalomethanes': 56.33,
            'Turbidity': 4.5
        }
    },
    {
        'id': 'hard_groundwater',
        'title': 'Nước ngầm phèn & độ đục cao (Không đạt)',
        'desc': 'Nước giếng khoan nhiễm phèn, pH = 4.1 rất chua, độ đục và TDS cao.',
        'values': {
            'ph': 4.1,
            'Hardness': 295.0,
            'Solids': 42000.0,
            'Chloramines': 4.5,
            'Sulfate': 450.0,
            'Conductivity': 680.0,
            'Organic_carbon': 18.2,
            'Trihalomethanes': 92.0,
            'Turbidity': 6.4
        }
    }
]

def get_model_and_preprocessor():
    """Loads and caches XGBoost model and preprocessor pipeline."""
    global _model, _preprocessor
    if _model is not None and _preprocessor is not None:
        return _model, _preprocessor

    # Find preprocessor
    prep_path = PREP_PATH_DIRECT if PREP_PATH_DIRECT.exists() else PREP_PATH_ROOT
    if not prep_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file preprocessor tại {prep_path}")
    
    # Find model
    model_path = MODEL_PATH_DIRECT if MODEL_PATH_DIRECT.exists() else MODEL_PATH_ROOT
    if not model_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file model tại {model_path}")

    _preprocessor = joblib.load(prep_path)
    _model = joblib.load(model_path)
    return _model, _preprocessor

def evaluate_metrics(input_data):
    """Đánh giá chi tiết từng chỉ tiêu nước theo quy chuẩn y tế/WHO."""
    evaluations = []
    issues = []
    goods = []

    for key in FEATURE_NAMES:
        val = input_data.get(key)
        std = METRIC_STANDARDS[key]
        
        if val is None or np.isnan(val):
            evaluations.append({
                'key': key,
                'name': std['name'],
                'value': None,
                'unit': std['unit'],
                'status': 'missing',
                'status_label': 'Chưa nhập',
                'standard': std['standard_desc'],
                'description': std['description'],
                'message': 'Giá trị khuyết thiếu - sẽ được mô hình ước lượng bằng trung vị (median).'
            })
            continue

        val_float = float(val)
        status = 'safe'
        status_label = 'Đạt chuẩn'
        msg = f"{std['name']} đạt ngưỡng khuyến cáo an toàn."

        if key == 'ph':
            if val_float < 6.5:
                status = 'danger'
                status_label = 'Quá chua (Axit)'
                msg = f"Độ pH = {val_float} < 6.5 (mang tính axit, có thể ăn mòn đường ống dẫn)."
                issues.append(msg)
            elif val_float > 8.5:
                status = 'warning'
                status_label = 'Quá kiềm (Bazo)'
                msg = f"Độ pH = {val_float} > 8.5 (kiềm cao, dễ đóng cặn và có vị đắng)."
                issues.append(msg)
            else:
                goods.append(f"pH ổn định ({val_float})")

        elif key == 'Turbidity':
            if val_float > 5.0:
                status = 'danger'
                status_label = 'Đục nặng'
                msg = f"Độ đục {val_float} NTU vượt ngưỡng 5.0 NTU (nhiều cặn bẩn, tiềm ẩn vi khuẩn)."
                issues.append(msg)
            elif val_float > 3.5:
                status = 'warning'
                status_label = 'Hơi đục'
                msg = f"Độ đục {val_float} NTU hơi cao so với tiêu chuẩn nước uống lý tưởng (< 1.0 NTU)."
            else:
                goods.append(f"Độ trong tốt ({val_float} NTU)")

        elif key == 'Trihalomethanes':
            if val_float > 80.0:
                status = 'danger'
                status_label = 'Vượt ngưỡng'
                msg = f"Nồng độ THMs = {val_float:.1f} μg/L > 80 μg/L (phụ phẩm khử trùng có nguy cơ độc tính)."
                issues.append(msg)
            else:
                goods.append(f"THMs an toàn ({val_float:.1f} μg/L)")

        elif key == 'Chloramines':
            if val_float > 8.0:
                status = 'danger'
                status_label = 'Rất cao'
                msg = f"Chloramines {val_float:.2f} ppm quá cao (mùi clo nồng, gây kích ứng)."
                issues.append(msg)
            elif val_float > 4.0:
                status = 'warning'
                status_label = 'Hơi cao'
                msg = f"Chloramines {val_float:.2f} ppm vượt mức khử trùng tiêu chuẩn (4.0 ppm)."
                issues.append(msg)
            else:
                goods.append(f"Clo dư an toàn ({val_float:.2f} ppm)")

        elif key == 'Hardness':
            if val_float > 250.0:
                status = 'warning'
                status_label = 'Nước cứng'
                msg = f"Độ cứng {val_float:.1f} mg/L ở mức cao, dễ gây bám cặn thiết bị."
            else:
                goods.append(f"Độ cứng hài hòa ({val_float:.1f} mg/L)")

        elif key == 'Solids':
            if val_float > 30000.0:
                status = 'warning'
                status_label = 'TDS rất cao'
                msg = f"Tổng chất rắn hòa tan TDS = {val_float:.0f} ppm rất cao."
                issues.append(msg)

        elif key == 'Sulfate':
            if val_float > 400.0:
                status = 'warning'
                status_label = 'Sunfat cao'
                msg = f"Nồng độ Sunfat {val_float:.1f} mg/L ở mức cao."

        evaluations.append({
            'key': key,
            'name': std['name'],
            'value': round(val_float, 2),
            'unit': std['unit'],
            'status': status,
            'status_label': status_label,
            'standard': std['standard_desc'],
            'description': std['description'],
            'message': msg
        })

    return evaluations, issues, goods

def predict_water_quality(input_dict):
    """
    Dự đoán chất lượng nước từ 9 chỉ số.
    Returns dictionary kết quả phân tích toàn diện.
    """
    model, preprocessor = get_model_and_preprocessor()

    # Chuẩn bị DataFrame với đúng tên và thứ tự cột
    row = {}
    for col in FEATURE_NAMES:
        val = input_dict.get(col)
        if val is None or val == '' or str(val).strip() == '':
            row[col] = np.nan
        else:
            try:
                row[col] = float(val)
            except (ValueError, TypeError):
                row[col] = np.nan

    df = pd.DataFrame([row], columns=FEATURE_NAMES)

    # Tiền xử lý (Median Imputer)
    clean_array = preprocessor.transform(df)

    # Dự đoán mô hình XGBoost
    pred = int(model.predict(clean_array)[0])
    probs = model.predict_proba(clean_array)[0]
    prob_non_potable = float(probs[0])
    prob_potable = float(probs[1])

    is_potable = (pred == 1)
    
    # Đánh giá chỉ số theo tiêu chuẩn y tế
    evaluations, issues, goods = evaluate_metrics(row)

    # Đề xuất giải pháp xử lý
    recommendations = []
    if is_potable:
        status_title = "NƯỚC ĐẠT CHUẨN AN TOÀN ĐỂ UỐNG (POTABLE)"
        status_color = "success"
        confidence = prob_potable * 100
        summary = f"Mô hình XGBoost dự đoán nguồn nước AN TOÀN để uống với xác suất tin cậy {confidence:.1f}%."
        recommendations.append("Nguồn nước đáp ứng tiêu chí cảm quan và hóa sinh cơ bản.")
        recommendations.append("Để đảm bảo vô trùng 100% khi uống trực tiếp, nên duy trì đun sôi hoặc lọc qua màng Nano/UF/RO định kỳ.")
    else:
        status_title = "NƯỚC KHÔNG AN TOÀN ĐỂ UỐNG (NON-POTABLE)"
        status_color = "danger"
        confidence = prob_non_potable * 100
        summary = f"Mô hình XGBoost đánh giá nguồn nước KHÔNG ĐẠT tiêu chuẩn uống trực tiếp (xác suất nguy cơ: {confidence:.1f}%)."
        
        # Đưa ra giải pháp xử lý tùy theo chỉ tiêu bất thường
        if any('pH' in issue or 'chua' in issue for issue in issues):
            recommendations.append("Cần bổ sung lõi lọc nâng pH (vật liệu lọc hạt Corosex hoặc lọc kiềm Hydro) để trung hòa axit.")
        if any('Turbidity' in issue or 'đục' in issue for issue in issues):
            recommendations.append("Cần qua cấp lọc thô sợi bông PP 1-5 micron hoặc bể lắng lọc cát thạch anh để loại bỏ cặn lơ lửng.")
        if any('THMs' in issue or 'Chloramines' in issue for issue in issues):
            recommendations.append("Cần sử dụng cột lọc Than Hoạt Tính khối đặc (Activated Carbon Block) để hấp phụ triệt để dư lượng Clo và Trihalomethanes.")
        if any('TDS' in issue or 'Sunfat' in issue or 'độ cứng' in issue for issue in issues):
            recommendations.append("Nên trang bị hệ thống lọc thẩm thấu ngược (RO - Reverse Osmosis) và màng làm mềm Cation để xử lý chất rắn hòa tan và kim loại.")
        if not recommendations:
            recommendations.append("Khuyến nghị đưa mẫu nước đến trung tâm kiểm nghiệm (Pasteur / Trung tâm Y tế Dự phòng) để xét nghiệm thêm chỉ tiêu vi sinh vật trước khi sử dụng.")

    return {
        'success': True,
        'prediction': pred,
        'is_potable': is_potable,
        'status_title': status_title,
        'status_color': status_color,
        'potability_score': round(prob_potable * 100, 2),
        'non_potability_score': round(prob_non_potable * 100, 2),
        'confidence': round(confidence, 2),
        'summary': summary,
        'metrics_evaluation': evaluations,
        'identified_issues': issues,
        'positive_points': goods,
        'recommendations': recommendations,
        'features_used': row
    }
