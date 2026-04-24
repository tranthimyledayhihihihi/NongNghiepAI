# 🌾 AgriAI - Hệ thống AI hỗ trợ nông dân

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)

Hệ thống AI toàn diện hỗ trợ nông dân Việt Nam trong việc dự báo thu hoạch, định giá nông sản thông minh, và kiểm tra chất lượng sản phẩm qua hình ảnh.

## ✨ Tính năng chính

### 🎯 MVP (Phase 1) - Đã hoàn thành

#### 1. 💰 Định giá nông sản thông minh
- ✅ Tra cứu giá hiện tại theo khu vực và chất lượng
- ✅ Dự báo giá 7-30 ngày tới với AI
- ✅ Phân tích xu hướng giá (tăng/giảm/ổn định)
- ✅ So sánh giá giữa các khu vực
- ✅ Lịch sử giá 30 ngày với biểu đồ
- ✅ Khuyến nghị thời điểm bán tối ưu

#### 2. 📸 Kiểm tra chất lượng qua ảnh
- ✅ Upload và phân tích ảnh nông sản
- ✅ AI phân loại chất lượng (Loại 1, 2, 3)
- ✅ Phát hiện khuyết tật tự động
- ✅ Đề xuất mức giá phù hợp theo chất lượng
- ✅ Khuyến nghị kênh bán hàng

### 🚧 Roadmap (Phase 2 & 3)

- [ ] Dự báo thời điểm thu hoạch tối ưu
- [ ] Thu thập giá thị trường tự động (crawler)
- [ ] Cảnh báo biến động giá qua Zalo/Email
- [ ] Tư vấn kênh bán hàng (thương lái, chợ, xuất khẩu)
- [ ] Mobile app (iOS & Android)
- [ ] Xác thực người dùng
- [ ] Dashboard analytics nâng cao

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQL Server (NongNghiepAI)
- **Cache**: Redis
- **AI/ML**: 
  - YOLOv8 (nhận diện chất lượng)
  - Scikit-learn (dự báo giá)
  - Prophet (dự báo thu hoạch)

### Frontend
- **Framework**: React + Vite
- **Styling**: Tailwind CSS
- **Charts**: Chart.js
- **State**: Zustand
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Database**: SQL Server (NongNghiepAI)
- **Cache**: Redis 7

## 📦 Cài đặt

### Yêu cầu
- SQL Server (2017+) hoặc SQL Server Express
- ODBC Driver 17 for SQL Server
- Node.js 20+ (nếu chạy local)
- Python 3.11+ (nếu chạy local)
- Redis (optional, for caching)

### 🚀 Quick Start với SQL Server

**Xem hướng dẫn chi tiết:** [QUICK_START_SQLSERVER.md](QUICK_START_SQLSERVER.md)

1. **Setup Database:**
```bash
python scripts/setup_sqlserver.py
```

2. **Test Connection:**
```bash
python backend/test_sqlserver_connection.py
```

3. **Start Application:**
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend (terminal mới)
cd frontend
npm run dev
```

4. **Truy cập:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Chạy với Docker (Coming Soon)

Docker setup đang được cập nhật cho SQL Server.

### Chạy local (Development)

#### 1. Cài đặt ODBC Driver
Download: https://go.microsoft.com/fwlink/?linkid=2249004

#### 2. Tạo Database
```sql
-- Trong SQL Server Management Studio
CREATE DATABASE NongNghiepAI;
GO
```

#### 3. Cấu hình .env
```bash
cp .env.example .env
```

Chỉnh sửa .env:
```env
DATABASE_URL=mssql+pyodbc://localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
REDIS_URL=redis://localhost:6379/0
CLAUDE_API_KEY=your_api_key_here
```

#### 4. Backend
```bash
cd backend
pip install -r requirements.txt
python ../scripts/setup_sqlserver.py
uvicorn app.main:app --reload
```

#### 5. Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📖 SQL Server Documentation

- **[QUICK_START_SQLSERVER.md](QUICK_START_SQLSERVER.md)** - 3-step quick start
- **[SQLSERVER_COMPLETE_GUIDE.md](SQLSERVER_COMPLETE_GUIDE.md)** - Full setup guide
- **[README_SQLSERVER.md](README_SQLSERVER.md)** - SQL Server overview
- **[NEXT_STEPS.md](NEXT_STEPS.md)** - What to do next

## 📚 API Documentation

Sau khi khởi động backend, truy cập:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Các endpoint chính:

#### Quality Check
- `POST /api/quality/check` - Kiểm tra chất lượng qua ảnh
- `GET /api/quality/grades` - Lấy danh sách phân loại

#### Pricing
- `POST /api/pricing/current` - Lấy giá hiện tại
- `POST /api/pricing/forecast` - Dự báo giá
- `GET /api/pricing/history/{crop_name}/{region}` - Lịch sử giá
- `GET /api/pricing/compare-regions/{crop_name}` - So sánh giá các vùng

## 🧪 Testing

### Test Backend
```bash
cd backend
pytest
```

### Test Frontend
```bash
cd frontend
npm run test
```

## 📁 Cấu trúc dự án

```
agri-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, database, redis
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── main.py       # FastAPI app
│   ├── ai_models/
│   │   ├── yolo_inference.py
│   │   └── price_forecast/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/     # API clients
│   │   └── App.jsx
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis
REDIS_URL=redis://host:port/db

# API Keys
CLAUDE_API_KEY=your_key
WEATHER_API_KEY=your_key

# Security
SECRET_KEY=your_secret_key
```

## 🚧 Roadmap

### Phase 2 (Upcoming)
- [ ] Dự báo thu hoạch
- [ ] Crawler dữ liệu thị trường
- [ ] Cảnh báo giá qua Zalo
- [ ] Tư vấn kênh bán hàng
- [ ] Authentication & Authorization

### Phase 3 (Future)
- [ ] Mobile app
- [ ] Tích hợp thêm nguồn dữ liệu
- [ ] Cải thiện AI models
- [ ] Multi-language support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 📧 Contact

For questions or support, please contact: [your-email@example.com]
