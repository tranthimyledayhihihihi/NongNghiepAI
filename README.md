# 🌾 AgriAI - Hệ thống AI hỗ trợ nông dân

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)

Hệ thống AI toàn diện hỗ trợ nông dân Việt Nam trong việc dự báo thu hoạch, định giá nông sản thông minh, và kiểm tra chất lượng sản phẩm qua hình ảnh.

## ✨ Tính năng & Trạng thái

### ✅ ĐÃ HOÀN THÀNH

#### 1. 🗄️ Database & Backend Infrastructure
- ✅ SQL Server database setup (10 tables)
- ✅ SQLAlchemy models (User, CropType, WeatherData, HarvestSchedule, MarketPrice, PriceHistory, PriceForecastResult, QualityRecord, AlertSubscription, AIConversation)
- ✅ FastAPI backend structure
- ✅ API endpoints (Quality, Pricing, Harvest, Market, Alert, Forecast)
- ✅ Database connection với SQL Server
- ✅ Redis client setup
- ✅ Security & authentication structure
- ✅ CORS configuration

#### 2. 💰 Định giá nông sản thông minh
- ✅ API endpoint lấy giá hiện tại (`/api/pricing/current`)
- ✅ API endpoint dự báo giá (`/api/pricing/forecast`)
- ✅ API endpoint lịch sử giá (`/api/pricing/history`)
- ✅ API endpoint so sánh giá vùng (`/api/pricing/compare-regions`)
- ✅ Pricing service với AI model structure
- ✅ Frontend: PriceInput component
- ✅ Frontend: PriceChart component
- ✅ Frontend: RegionCompare component
- ✅ Frontend: PricingPage

#### 3. 📸 Kiểm tra chất lượng qua ảnh
- ✅ API endpoint kiểm tra chất lượng (`/api/quality/check`)
- ✅ API endpoint lấy danh sách phân loại (`/api/quality/grades`)
- ✅ YOLO inference structure
- ✅ Image upload handling
- ✅ Frontend: ImageUpload component
- ✅ Frontend: QualityResult component
- ✅ Frontend: QualityCheckPage

#### 4. 🌾 Dự báo thu hoạch
- ✅ API endpoint dự báo thu hoạch (`/api/harvest/forecast`)
- ✅ API endpoint lấy danh sách crops (`/api/harvest/crops`)
- ✅ Prophet model structure
- ✅ Harvest service
- ✅ Frontend: HarvestForm component
- ✅ Frontend: HarvestResult component
- ✅ Frontend: HarvestForecastPage

#### 5. � Hệ thống cảnh báo
- ✅ API endpoint đăng ký cảnh báo (`/api/alert/subscribe`)
- ✅ API endpoint lấy lịch sử cảnh báo (`/api/alert/history`)
- ✅ Alert service structure
- ✅ Frontend: AlertSubscribe component
- ✅ Frontend: AlertHistory component
- ✅ Frontend: AlertPage

#### 6. 📊 Thị trường & Phân tích
- ✅ API endpoint phân tích thị trường (`/api/market/analysis`)
- ✅ API endpoint gợi ý kênh bán (`/api/market/suggest-channel`)
- ✅ Market service
- ✅ Frontend: MarketSuggest component
- ✅ Frontend: ChannelCompare component

#### 7. 🎨 Frontend UI/UX
- ✅ React + Vite setup
- ✅ Tailwind CSS styling
- ✅ Responsive layout
- ✅ Navbar component
- ✅ Sidebar component
- ✅ LoadingSpinner component
- ✅ Dashboard page
- ✅ Routing setup (React Router)
- ✅ API services (axios)
- ✅ State management (Zustand stores)
- ✅ Custom hooks (useWebSocket, useHarvest, usePriceData)

#### 8. 📚 Documentation
- ✅ README.md - Main documentation
- ✅ START_HERE.md - Quick start guide
- ✅ USER_SCHEMA_GUIDE.md - Database schema
- ✅ API_DOCUMENTATION.md - API reference
- ✅ DOCS.md - Documentation index
- ✅ CONTRIBUTING.md - Contribution guide
- ✅ CHANGELOG.md - Version history
- ✅ DEPLOYMENT.md - Deploy guide
- ✅ TODO.md - Future tasks

#### 9. 🔧 Development Tools
- ✅ SQL Server setup script
- ✅ Connection test script
- ✅ Seed data (3 crop types, sample prices)
- ✅ Stored procedures (sp_GetPriceHistory, sp_GetHarvestForecast, sp_UpdateMarketPrice)
- ✅ Environment configuration (.env)
- ✅ Requirements.txt (Python dependencies)
- ✅ Package.json (Node dependencies)

---

### 🚧 CHƯA HOÀN THÀNH / CẦN PHÁT TRIỂN

#### 1. 🤖 AI Models Training & Integration
- ⏳ **YOLOv8 Model Training** - Cần train model với dữ liệu nông sản Việt Nam
  - Chưa có dataset ảnh nông sản
  - Chưa train model
  
  - Chưa có weights file
- ⏳ **Price Forecasting Model** - Cần train với dữ liệu giá thực tế
  - Chưa có dữ liệu lịch sử giá đầy đủ
  - Model structure có sẵn nhưng chưa train
- ⏳ **Harvest Forecasting Model** - Cần train với dữ liệu mùa vụ
  - Prophet model structure có sẵn
  - Chưa có dữ liệu training
  - Chưa tích hợp dữ liệu thời tiết

#### 2. 🕷️ Data Crawler System
- ⏳ **Crawler Implementation** - Thu thập giá thị trường tự động
  - Scrapy structure có sẵn
  - Chưa implement spider logic cho:
    - agro.gov.vn
    - gia.vn
    - Báo Nông nghiệp VN
  - Chưa có Celery tasks cho scheduled crawling
  - Chưa có data pipeline

#### 3. 🔐 Authentication & Authorization
- ⏳ **User Authentication**
  - Security structure có sẵn
  - Chưa implement login/register endpoints
  - Chưa có JWT token handling
  - Chưa có password hashing
- ⏳ **User Management**
  - Chưa có user profile management
  - Chưa có role-based access control

#### 4. 📧 Notification System
- ⏳ **Zalo Integration**
  - ZaloID field có trong database
  - Chưa implement Zalo API
  - Chưa có Zalo notification service
- ⏳ **Email Notifications**
  - Chưa có email service
  - Chưa có email templates
- ⏳ **Real-time Alerts**
  - WebSocket structure có sẵn
  - Chưa implement real-time price alerts

#### 5. 🌤️ Weather Integration
- ⏳ **Weather API Integration**
  - Weather service structure có sẵn
  - Chưa implement weather API calls
  - Chưa tích hợp vào harvest forecast

#### 6. 🧪 Testing
- ⏳ **Backend Tests**
  - Test structure có sẵn (pytest.ini)
  - Chưa có unit tests
  - Chưa có integration tests
- ⏳ **Frontend Tests**
  - Chưa có component tests
  - Chưa có E2E tests

#### 7. 🐳 Docker & Deployment
- ⏳ **Docker Setup**
  - Dockerfile có sẵn
  - docker-compose.yml cần cập nhật cho SQL Server
  - Chưa test Docker deployment
- ⏳ **Production Deployment**
  - Chưa có CI/CD pipeline
  - Chưa có production configuration
  - Chưa có monitoring setup

#### 8. 📱 Mobile App
- ⏳ **iOS App** - Chưa bắt đầu
- ⏳ **Android App** - Chưa bắt đầu
- ⏳ **React Native** - Chưa setup

#### 9. 📊 Analytics & Reporting
- ⏳ **Dashboard Analytics**
  - Dashboard page có sẵn
  - Chưa có charts & metrics
  - Chưa có real-time data
- ⏳ **Reports Generation**
  - Chưa có report templates
  - Chưa có export functionality

#### 10. 🌐 Additional Features
- ⏳ **Multi-language Support** - Chỉ có tiếng Việt
- ⏳ **Offline Mode** - Chưa có
- ⏳ **Data Export** - Chưa có (CSV, Excel, PDF)
- ⏳ **Advanced Search** - Chưa có
- ⏳ **Favorites/Bookmarks** - Chưa có

---

### 📊 Tổng Kết Tiến Độ

**Hoàn thành:** ~60%
- ✅ Database & Backend Structure: 100%
- ✅ API Endpoints: 100%
- ✅ Frontend UI: 100%
- ✅ Documentation: 100%
- ⏳ AI Models: 20% (structure only)
- ⏳ Data Crawler: 20% (structure only)
- ⏳ Authentication: 30% (structure only)
- ⏳ Notifications: 10% (structure only)
- ⏳ Testing: 5%
- ⏳ Deployment: 30%

**Ưu tiên tiếp theo:**
1. 🤖 Train AI models với dữ liệu thực
2. 🕷️ Implement data crawlers
3. 🔐 Complete authentication system
4. 🧪 Add comprehensive testing
5. 🐳 Setup production deployment

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

## 📚 Documentation

For detailed documentation, see:
- **[DOCS.md](DOCS.md)** - Complete documentation index
- **[START_HERE.md](START_HERE.md)** - Quick start guide
- **[USER_SCHEMA_GUIDE.md](USER_SCHEMA_GUIDE.md)** - Database schema guide
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference

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

- **[START_HERE.md](START_HERE.md)** - Quick start guide
- **[USER_SCHEMA_GUIDE.md](USER_SCHEMA_GUIDE.md)** - Database schema guide
- **[DOCS.md](DOCS.md)** - Complete documentation index

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

## � Roadmap & Next Steps

### 🎯 Immediate Priorities (Phase 2)

1. **🤖 AI Models Training**
   - Collect Vietnamese crop image dataset
   - Train YOLOv8 for quality detection
   - Train price forecasting model with real data
   - Integrate weather data for harvest prediction

2. **🕷️ Data Crawler Implementation**
   - Implement spiders for agro.gov.vn, gia.vn
   - Setup Celery for scheduled crawling
   - Build data pipeline and validation

3. **🔐 Authentication System**
   - Implement login/register endpoints
   - Add JWT token handling
   - User profile management
   - Role-based access control

4. **📧 Notification System**
   - Zalo API integration
   - Email service setup
   - Real-time price alerts via WebSocket

5. **🧪 Testing & Quality**
   - Unit tests for backend
   - Integration tests
   - Frontend component tests
   - E2E testing

### 🔮 Future Plans (Phase 3)

- 📱 Mobile app (React Native)
- 🌐 Multi-language support
- 📊 Advanced analytics dashboard
- 🐳 Production deployment with Docker
- 🔄 CI/CD pipeline
- 📈 Performance monitoring
- 🌍 Multi-region support
- 🤝 Third-party integrations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 📧 Contact

**Project Maintainer:** Trần Thị Mỹ

For questions or support, please contact: [tranthimy2205@gmail.com](mailto:tranthimy2205@gmail.com)

---

**Built with ❤️ for Vietnamese farmers**
