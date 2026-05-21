# README Docker - NongNghiepAI

Tài liệu này giúp chạy toàn bộ dự án bằng Docker, không phụ thuộc Python/Node/SQL Server cài trực tiếp trên máy cá nhân.

## Kiến trúc dự án

- **Backend:** FastAPI + Uvicorn, SQLAlchemy, Celery/Redis, chạy tại `http://localhost:8000`.
- **Frontend:** React 18 + Vite 5 + Tailwind CSS, chạy tại `http://localhost:5173`.
- **Database:** SQL Server 2022 container, database mặc định `NongNghiepAI`, port host `1433`.
- **Cache/queue:** Redis 7 container, port host `6379`.

## File Docker chính

- `backend/Dockerfile`: build Python 3.11, cài dependencies từ `backend/requirements.txt`, expose `8000`.
- `frontend/Dockerfile`: build Node 20, cài dependencies bằng `npm ci`, expose `5173`.
- `docker-compose.yml`: chạy `database`, `db-init`, `redis`, `backend`, `frontend` trên cùng network mặc định của Compose; `worker` là profile tùy chọn.
- `.env.example`: mẫu biến môi trường, không chứa API key thật.
- `.dockerignore`, `backend/.dockerignore`, `frontend/.dockerignore`: loại cache, virtualenv, node_modules, build output, file tạm.

## Chạy nhanh

```bash
cp .env.example .env
docker compose up --build
```

Nếu dùng PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Sau khi chạy:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Database test: http://localhost:8000/db-test

## Các lệnh thường dùng

Build image:

```bash
docker compose build
```

Chạy foreground:

```bash
docker compose up
```

Chạy nền:

```bash
docker compose up -d
```

Xem log:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f database
docker compose logs -f db-init
```

Chạy thêm Celery worker nếu cần task queue riêng:

```bash
docker compose --profile worker up
```

Dừng container:

```bash
docker compose down
```

Dừng và xóa volume database/cache:

```bash
docker compose down -v
```

Rebuild khi đổi dependency:

```bash
docker compose build --no-cache backend
docker compose build --no-cache frontend
docker compose up
```

## Cấu hình `.env`

Tạo `.env` từ `.env.example`, sau đó chỉnh các biến cần thiết:

- `MSSQL_SA_PASSWORD`: mật khẩu SA của SQL Server container.
- `DATABASE_URL`: backend dùng `database` làm hostname trong Docker, ví dụ `mssql+pymssql://sa:YourStrongPassword123!@database:1433/NongNghiepAI`.
- `SECRET_KEY`: đổi khi chạy thật.
- `GOOGLE_API_KEY` hoặc `GEMINI_API_KEY`: cần cho Gemini/AI chat.
- `TAVILY_API_KEY`: cần nếu bật Tavily search/news.
- `VITE_API_BASE_URL`: mặc định để trống để frontend gọi `/api/...` qua Vite proxy.
- `VITE_BACKEND_PROXY_URL`: trong Docker giữ `http://backend:8000`.

Nếu đổi `MSSQL_SA_PASSWORD`, hãy đổi đồng bộ mật khẩu trong `DATABASE_URL`.

## Database init

Service `db-init` tự chờ SQL Server sẵn sàng rồi chạy `NongNghiepAI_Full.sql` lần đầu. Nếu database đã có bảng, `db-init` sẽ bỏ qua để tránh xóa dữ liệu.

Muốn reset database từ đầu:

```bash
FORCE_DB_INIT=true docker compose up --force-recreate db-init
```

Hoặc trên PowerShell:

```powershell
$env:FORCE_DB_INIT="true"; docker compose up --force-recreate db-init
```

Lưu ý: reset bằng SQL script sẽ xóa và tạo lại bảng/dữ liệu seed.

## Frontend gọi backend

Trong Docker, browser gọi frontend tại `localhost:5173`; frontend dùng đường dẫn tương đối `/api/...`, Vite proxy trong container chuyển tiếp đến `http://backend:8000`. Vì vậy không cần hardcode `localhost` trong code frontend.

Nếu muốn bỏ proxy và gọi backend trực tiếp từ browser, đặt:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Dùng database ngoài Docker

Dự án đã cấu hình SQL Server container mặc định. Nếu muốn dùng SQL Server ngoài Docker:

1. Đảm bảo SQL Server ngoài máy host/container network có thể truy cập được.
2. Sửa `DATABASE_URL` trong `.env` sang hostname/IP thật, không dùng `localhost` nếu backend vẫn chạy trong container.
3. Có thể tắt service `database` và `db-init` bằng compose override riêng.

Ví dụ khi SQL Server chạy trên host Windows, Docker Desktop thường dùng:

```env
DATABASE_URL=mssql+pymssql://sa:your-password@host.docker.internal:1433/NongNghiepAI
```

## Xử lý lỗi thường gặp

- **Port bị chiếm:** đổi `FRONTEND_PORT`, `BACKEND_PORT`, `MSSQL_PORT`, `REDIS_PORT` trong `.env`.
- **SQL Server không lên:** kiểm tra `MSSQL_SA_PASSWORD` đủ mạnh và xem `docker compose logs -f database`.
- **Backend không kết nối DB:** chạy `docker compose logs -f db-init backend`; trong Docker phải dùng hostname `database`.
- **Frontend gọi API lỗi:** giữ `VITE_API_BASE_URL=` rỗng và `VITE_BACKEND_PROXY_URL=http://backend:8000`, sau đó rebuild frontend.
- **Đổi package Python/Node:** chạy `docker compose build --no-cache backend frontend`.
- **Thiếu API key:** app vẫn chạy, nhưng các tính năng AI/Tavily có thể trả lỗi cấu hình rõ ràng cho đến khi điền key.

## Ghi chú phát triển

- Backend mount `./backend:/app` và chạy `uvicorn --reload` để tự reload khi sửa code.
- Frontend mount `./frontend:/app`, dùng volume `frontend_node_modules` để không phụ thuộc `node_modules` trên máy host.
- Upload được lưu ở `./storage/uploads` thông qua volume vào `/app/storage/uploads`.
- Docker mặc định đặt `ALLOW_MOCK_DATA=false`, `ALLOW_SAMPLE_DATA=false`, `USE_REALTIME_ONLY=true` để không che lỗi API/database bằng dữ liệu mẫu.
