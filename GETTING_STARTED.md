# 🚀 Getting Started với AgriAI

## Giới thiệu

AgriAI là hệ thống AI hỗ trợ nông dân với các tính năng:
- 🌾 Dự báo giá nông sản
- 📸 Kiểm tra chất lượng qua ảnh
- 📊 Phân tích xu hướng thị trường
- 💰 Đề xuất giá bán phù hợp

## Yêu cầu hệ thống

- **Docker Desktop** (Windows/Mac) hoặc **Docker Engine** (Linux)
- **Git** để clone repository
- **4GB RAM** tối thiểu
- **10GB** dung lượng ổ cứng

## Cài đặt nhanh (5 phút)

### Bước 1: Clone repository

```bash
git clone https://github.com/your-username/agri-ai.git
cd agri-ai
```

### Bước 2: Chạy script setup

**Linux/Mac:**
```bash
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/start.sh
```

**Windows (Git Bash):**
```bash
bash scripts/setup.sh
bash scripts/start.sh
```

**Windows (PowerShell):**
```powershell
docker-compose up -d
```

### Bước 3: Truy cập ứng dụng

Đợi khoảng 30 giây để services khởi động, sau đó:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Hướng dẫn sử dụng

### 1. Kiểm tra chất lượng nông sản

1. Truy cập http://localhost:5173/quality
2. Click "Chọn ảnh" và upload ảnh nông sản
3. Click "Kiểm tra chất lượng"
4. Xem kết quả phân tích:
   - Phân loại chất lượng (Loại 1, 2, 3)
   - Độ tin cậy
   - Khuyết tật phát hiện
   - Giá đề xuất

### 2. Tra cứu và dự báo giá

1. Truy cập http://localhost:5173/pricing
2. Chọn:
   - Loại nông sản (Cà chua, Dưa chuột, v.v.)
   - Khu vực (Hà Nội, TP.HCM, v.v.)
   - Số ngày dự báo (7, 14, 30 ngày)
3. Click "Tra cứu"
4. Xem:
   - Giá hiện tại
   - Xu hướng giá
   - Biểu đồ dự báo
   - Khuyến nghị bán hàng

### 3. Sử dụng API trực tiếp

#### Kiểm tra chất lượng:
```bash
curl -X POST http://localhost:8000/api/quality/check \
  -F "file=@/path/to/image.jpg"
```

#### Dự báo giá:
```bash
curl -X POST http://localhost:8000/api/pricing/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "crop_name": "Cà chua",
    "region": "Hà Nội",
    "days": 7
  }'
```

## Khởi tạo dữ liệu mẫu

Để có dữ liệu test:

```bash
# Vào container backend
docker-compose exec backend bash

# Chạy script init
python scripts/init_db.py
```

## Troubleshooting

### Port đã được sử dụng

Nếu gặp lỗi port conflict:

1. Kiểm tra port đang dùng:
```bash
# Linux/Mac
lsof -i :8000
lsof -i :5173

# Windows
netstat -ano | findstr :8000
```

2. Dừng service đang dùng port hoặc đổi port trong `docker-compose.yml`

### Container không start

```bash
# Xem logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart

# Rebuild nếu cần
docker-compose up -d --build
```

### Database connection error

```bash
# Restart database
docker-compose restart db

# Xem logs database
docker-compose logs db

# Xóa và tạo lại
docker-compose down -v
docker-compose up -d
```

## Dừng hệ thống

```bash
# Dừng services
docker-compose down

# Hoặc dùng script
./scripts/stop.sh
```

## Xóa toàn bộ (bao gồm data)

```bash
docker-compose down -v
```

## Tiếp theo

- Đọc [API Documentation](API_DOCUMENTATION.md) để tìm hiểu chi tiết API
- Xem [TODO.md](TODO.md) để biết roadmap
- Đọc [CONTRIBUTING.md](CONTRIBUTING.md) nếu muốn đóng góp

## Cần trợ giúp?

- Mở issue trên GitHub
- Xem documentation trong thư mục `docs/`
- Liên hệ qua email

Chúc bạn sử dụng AgriAI hiệu quả! 🌾
