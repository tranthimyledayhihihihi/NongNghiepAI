# 🚀 Quick Start Guide

## Khởi động nhanh với Docker

### 1. Cài đặt Docker
Đảm bảo bạn đã cài Docker và Docker Compose:
- Windows/Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Linux: Docker Engine + Docker Compose

### 2. Clone và khởi động

```bash
# Clone repository
git clone <your-repo-url>
cd agri-ai

# Khởi động tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f
```

### 3. Truy cập ứng dụng

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Test các tính năng

#### Test API với curl:

```bash
# Health check
curl http://localhost:8000/health

# Get current price
curl -X POST http://localhost:8000/api/pricing/current \
  -H "Content-Type: application/json" \
  -d '{"crop_name":"Cà chua","region":"Hà Nội","quality_grade":"grade_1"}'

# Price forecast
curl -X POST http://localhost:8000/api/pricing/forecast \
  -H "Content-Type: application/json" \
  -d '{"crop_name":"Cà chua","region":"Hà Nội","days":7}'
```

#### Test Quality Check:
1. Mở http://localhost:5173/quality
2. Upload ảnh nông sản
3. Nhấn "Kiểm tra chất lượng"

## Dừng hệ thống

```bash
# Dừng tất cả services
docker-compose down

# Dừng và xóa volumes (database data)
docker-compose down -v
```

## Troubleshooting

### Port đã được sử dụng
Nếu port 5432, 6379, 8000, hoặc 5173 đã được sử dụng, chỉnh sửa `docker-compose.yml`

### Database connection error
```bash
# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Frontend không kết nối được backend
Kiểm tra CORS settings trong `backend/app/core/config.py`
