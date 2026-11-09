import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ml_service import (
    predict_water_quality,
    PRESET_SAMPLES,
    METRIC_STANDARDS,
    FEATURE_NAMES
)

@csrf_exempt
def predict_view(request):
    """API Endpoint nhận các thông số nước và trả về kết quả đánh giá."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Chỉ chấp nhận phương thức POST'}, status=405)
    
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        result = predict_water_quality(data)
        return JsonResponse(result, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Lỗi trong quá trình xử lý: {str(e)}'}, status=500)

def presets_view(request):
    """API Endpoint trả về danh sách mẫu thử có sẵn và tiêu chuẩn từng chỉ số."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Chỉ chấp nhận phương thức GET'}, status=405)
        
    return JsonResponse({
        'presets': PRESET_SAMPLES,
        'standards': METRIC_STANDARDS,
        'features': FEATURE_NAMES
    }, status=200)

def stats_view(request):
    """API Endpoint trả về thông tin mô hình XGBoost và số liệu tổng quan."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Chỉ chấp nhận phương thức GET'}, status=405)

    return JsonResponse({
        'model_name': 'XGBoost Classifier (Extreme Gradient Boosting)',
        'framework': 'XGBoost 3.x + Scikit-Learn',
        'hyperparameters': {
            'n_estimators': 1000,
            'max_depth': 5,
            'learning_rate': 0.01,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'eval_metric': 'logloss'
        },
        'features_count': len(FEATURE_NAMES),
        'target': 'Potability (0: Không an toàn, 1: An toàn)',
        'data_source': 'water_potability.csv (3,276 mẫu nước nghiên cứu)'
    }, status=200)
