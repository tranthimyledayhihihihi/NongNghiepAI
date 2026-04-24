# 📚 AgriAI Documentation

## 📖 Tài Liệu Dự Án

### 🚀 Bắt Đầu Nhanh
- **[START_HERE.md](START_HERE.md)** - Hướng dẫn bắt đầu nhanh với SQL Server
- **[README.md](README.md)** - Tổng quan dự án và cài đặt

### 🗄️ Database
- **[USER_SCHEMA_GUIDE.md](USER_SCHEMA_GUIDE.md)** - Hướng dẫn chi tiết về database schema
- **[nongnghiepAI.sql](nongnghiepAI.sql)** - SQL script tạo database

### 🔌 API
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Chi tiết các API endpoints
- **API Docs (Live):** http://localhost:8000/docs

### 🛠️ Development
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Hướng dẫn đóng góp code
- **[CHANGELOG.md](CHANGELOG.md)** - Lịch sử thay đổi
- **[TODO.md](TODO.md)** - Danh sách công việc cần làm

### 🚢 Deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Hướng dẫn triển khai production

---

## 🎯 Quick Links

### Setup Database
```bash
# Chạy SQL script trong SSMS
# File: nongnghiepAI.sql
```

### Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### Access Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📞 Contact

**Project Maintainer:** Trần Thị Mỹ  
**Email:** [tranthimy2205@gmail.com](mailto:tranthimy2205@gmail.com)

---

## 📁 Project Structure

```
agri-ai/
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   ├── ai_models/       # AI models (YOLO, Prophet)
│   └── crawler/         # Data crawlers
│
├── frontend/            # React frontend
│   ├── src/            # Source code
│   └── public/         # Static files
│
├── data/               # Database files
│   ├── tables/        # Table definitions
│   ├── seeds/         # Seed data
│   └── stored_procedures/  # SQL procedures
│
└── docs/              # Documentation (this folder)
```

---

## 🔑 Key Features

1. **Quality Check** - AI-powered crop quality assessment
2. **Price Forecasting** - Predict market prices
3. **Harvest Planning** - Optimize harvest schedules
4. **Market Analysis** - Compare prices across regions
5. **Alert System** - Price change notifications

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.11+
- **Frontend:** React 18, Vite, Tailwind CSS
- **Database:** SQL Server
- **AI/ML:** YOLOv8, Scikit-learn, Prophet
- **Cache:** Redis

---

**Built with ❤️ for Vietnamese farmers**
