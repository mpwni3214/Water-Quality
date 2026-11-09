# 💧 Hệ Thống Đánh Giá Chất Lượng Nước (Water Quality Assessment)
### Ứng dụng Web dự đoán độ an toàn nguồn nước (Potability) với Django REST API & React Vite

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/mpwni3214/Water-Quality)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.0%2B-darkgreen?logo=django)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18%2B-blue?logo=react)](https://react.dev/)
[![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange)](https://xgboost.readthedocs.io/)

Ứng dụng web được xây dựng dựa trên mô hình **XGBoost Classifier** đã được huấn luyện trên bộ dữ liệu `water_potability.csv` (3,276 mẫu nước nghiên cứu) kết hợp bộ tiền xử lý `water_preprocessor.pkl` (Median Imputer). Ngoài việc dự đoán nhãn nhị phân (Uống được / Không uống được) và xác suất tin cậy, hệ thống còn **đối chiếu 9 chỉ số hóa sinh với quy chuẩn an toàn nước sạch của WHO và QCVN 01-1:2018/BYT**, tự động chẩn đoán các thông số bất thường và đề xuất giải pháp xử lý kỹ thuật (lọc RO, than hoạt tính, nâng pH...).

---

## 📥 Cài Đặt Khi Clone Dự Án Về Máy

```powershell
# 1. Clone repository
git clone https://github.com/mpwni3214/Water-Quality.git
cd Water-Quality

# 2. Tạo virtualenv và cài đặt backend dependencies
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 3. Cài đặt frontend dependencies
cd frontend
npm install
cd ..
```

---

## 🏗️ Kiến Trúc Hệ Thống

```
Water Quality/
│
├── Water_quality.ipynb         # Jupyter Notebook huấn luyện & đánh giá mô hình XGBoost
├── water_potability.csv        # Tập dữ liệu gốc 3,276 mẫu nước
├── water_preprocessor.pkl      # Pipeline xử lý khuyết thiếu (SimpleImputer median)
├── xgboost_water_model.pkl     # Mô hình XGBoost đã huấn luyện
│
├── backend/                    # Backend Django (REST API)
│   ├── manage.py
│   ├── backend/                # Cấu hình dự án Django, CORS, URL routing
│   │   ├── settings.py
│   │   └── urls.py
│   ├── api/                    # Ứng dụng xử lý API & dự đoán Machine Learning
│   │   ├── ml_service.py       # Tải model, nạp pipeline, dự đoán & chẩn đoán ngưỡng
│   │   ├── views.py            # API View /api/predict/, /api/presets/, /api/stats/
│   │   └── urls.py
│   └── models/                 # Thư mục lưu bản sao mô hình cho backend
│
├── frontend/                   # Frontend React (Vite + Modern UI + Lucide Icons)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts          # Cấu hình proxy đến backend Django
│   └── src/
│       ├── main.jsx            # Entry point React 18+
│       ├── App.jsx             # Giao diện chính: Form nhập liệu, Preset, Kết quả & Lịch sử
│       └── index.css           # Giao diện hiện đại phong cách Dark Glassmorphism
│
├── run_all.bat                 # Script chạy nhanh cả Backend và Frontend (Windows batch)
├── run_all.ps1                 # Script chạy nhanh qua PowerShell
├── run_backend.bat             # Chạy riêng Backend Django (Port 8000)
└── run_frontend.bat            # Chạy riêng Frontend React (Port 5173)
```

---

## ⚡ Hướng Dẫn Khởi Động Nhanh (Quick Start)

### Cách 1: Khởi động tự động bằng 1 cú nhấp chuột (Khuyên dùng)
Nhấp đúp chuột vào file:
👉 **`run_all.bat`** (hoặc chuột phải vào `run_all.ps1` chọn *Run with PowerShell*)

Hệ thống sẽ tự động bật 2 cửa sổ terminal:
- **Backend Django**: `http://127.0.0.1:8000`
- **Frontend React**: `http://localhost:5173`

Sau khi khởi chạy, mở trình duyệt truy cập: **`http://localhost:5173`**

---

### Cách 2: Khởi động thủ công bằng dòng lệnh

#### 1. Khởi động Backend (Django)
```powershell
cd "c:\Users\Admin\Documents\AI_Projects\Water Quality\backend"
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

#### 2. Khởi động Frontend (React Vite)
Mở một cửa sổ Terminal mới:
```powershell
cd "c:\Users\Admin\Documents\AI_Projects\Water Quality\frontend"
npm run dev
```

Truy cập: **`http://localhost:5173`**

---

## 📡 Danh Sách API Endpoints (Backend Django)

| Phương thức | Đường dẫn | Chức năng | Định dạng gửi |
|---|---|---|---|
| `POST` | `/api/predict/` | Nhận 9 chỉ số nước, trả về nhãn an toàn, xác suất %, đánh giá chi tiết và khuyến nghị xử lý | JSON |
| `GET` | `/api/presets/` | Trả về danh sách mẫu thử thực tế và quy chuẩn WHO của 9 chỉ số | - |
| `GET` | `/api/stats/` | Trả về thông số siêu tham số mô hình XGBoost và metadata dữ liệu | - |

### Ví dụ dữ liệu gửi đến `/api/predict/`:
```json
{
  "ph": 7.25,
  "Hardness": 180.5,
  "Solids": 18500.0,
  "Chloramines": 6.2,
  "Sulfate": 310.0,
  "Conductivity": 390.0,
  "Organic_carbon": 11.5,
  "Trihalomethanes": 55.0,
  "Turbidity": 3.1
}
```

### Ví dụ kết quả phản hồi:
```json
{
  "success": true,
  "is_potable": false,
  "potability_score": 24.65,
  "status_title": "NƯỚC KHÔNG AN TOÀN ĐỂ UỐNG (NON-POTABLE)",
  "status_color": "danger",
  "summary": "Mô hình XGBoost đánh giá nguồn nước KHÔNG ĐẠT tiêu chuẩn uống trực tiếp (xác suất nguy cơ: 75.3%).",
  "metrics_evaluation": [ ... ],
  "recommendations": [
    "Cần sử dụng cột lọc Than Hoạt Tính khối đặc (Activated Carbon Block) để hấp phụ triệt để dư lượng Clo và Trihalomethanes."
  ]
}
```

---

## 🧪 9 Chỉ Số Chất Lượng Nước & Quy Chuẩn Đối Chiếu

| STT | Tên chỉ số | Tên khoa học | Đơn vị | Ngưỡng an toàn khuyến cáo (WHO / QCVN) | Ý nghĩa kỹ thuật |
|---|---|---|---|---|---|
| 1 | **Độ pH** | `ph` | pH | **6.5 – 8.5** | Đo độ axit/kiềm. < 6.5 ăn mòn kim loại; > 8.5 gây đắng & đóng cặn. |
| 2 | **Độ cứng** | `Hardness` | mg/L | **< 300 mg/L** | Lượng muối Canxi và Magie hòa tan; quá cao gây tắc nghẽn đường ống. |
| 3 | **Tổng chất rắn hòa tan** | `Solids` | ppm | **< 500 – 1000 ppm** | Tổng hàm lượng khoáng và kim loại; trên 1000 ppm có mùi vị bất thường. |
| 4 | **Chloramines** | `Chloramines` | ppm | **< 4.0 ppm** | Dư lượng hợp chất Clo khử khuẩn; quá cao gây kích ứng và mùi hắc. |
| 5 | **Sunfat** | `Sulfate` | mg/L | **< 250 mg/L** | Nồng độ muối sunfat tự nhiên trong đất đá; > 250 mg/L gây vị lạ. |
| 6 | **Độ dẫn điện** | `Conductivity` | μS/cm | **< 400 – 750 μS/cm** | Khả năng dẫn điện đo nồng độ ion tự do. |
| 7 | **Cacbon hữu cơ tổng** | `Organic_carbon`| ppm | **< 2.0 – 4.0 ppm** | Thước đo chất hữu cơ phân hủy sinh học (TOC); mức cao nuôi vi khuẩn. |
| 8 | **Trihalomethanes** | `Trihalomethanes`| μg/L | **< 80 μg/L** | Phụ phẩm clo hóa độc hại sinh ra do Clo phản ứng với chất hữu cơ. |
| 9 | **Độ đục** | `Turbidity` | NTU | **< 5.0 NTU (lý tưởng < 1.0)** | Đo độ trong suốt; nước đục tiềm ẩn mầm bệnh và cặn lơ lửng. |

---

## ✨ Tính Năng Nổi Bật Của Giao Diện Web React

1. **Preset Mẫu Thử Nhanh (1-Click)**: Tích hợp sẵn các mẫu nước thực nghiệm (Nước đạt chuẩn, nước kiềm an toàn, nước máy dư clo & THMs, nước ngầm nhiễm phèn) để người dùng thử nghiệm nhanh mà không cần nhập thủ công 9 số.
2. **Đồng Hồ Xác Suất Trực Quan**: Hiển thị thanh đo tỷ lệ % Potability an toàn theo thời gian thực với mã màu xanh (Safe) / đỏ (Unsafe).
3. **Chẩn Đoán Từng Thông Số**: Đánh giá chi tiết từng chỉ tiêu (Đạt chuẩn / Chú ý / Vượt ngưỡng) với thẻ thông tin chuyên nghiệp.
4. **Đề Xuất Khắc Phục Kỹ Thuật**: Đưa ra giải pháp xử lý nước thực tế (hạt nâng pH, cột than hoạt tính, màng RO, lắng lọc...).
5. **Lịch Sử Đánh Giá**: Tự động lưu lại các lần đo gần nhất để so sánh và nhấp chọn lại nhanh chóng.

