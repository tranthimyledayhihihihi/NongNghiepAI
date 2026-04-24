# ✅ Verification Checklist

Checklist để verify hệ thống AgriAI hoạt động đúng.

## 🔧 Pre-requisites

- [ ] Docker Desktop đã cài đặt
- [ ] Docker đang chạy
- [ ] Git đã cài đặt
- [ ] Port 5432, 6379, 8000, 5173 không bị chiếm

## 📦 Installation

- [ ] Clone repository thành công
- [ ] File .env đã được tạo
- [ ] Thư mục uploads đã được tạo

## 🚀 Startup

- [ ] `docker-compose up -d` chạy thành công
- [ ] Tất cả 4 containers đang chạy:
  - [ ] agridb (PostgreSQL)
  - [ ] agriredis (Redis)
  - [ ] agri_backend
  - [ ] agri_frontend
- [ ] Không có error trong logs

## 🌐 Accessibility

### Frontend
- [ ] http://localhost:5173 accessible
- [ ] Trang Dashboard hiển thị đúng
- [ ] Navigation menu hoạt động
- [ ] Không có console errors

### Backend
- [ ] http://localhost:8000 accessible
- [ ] http://localhost:8000/docs hiển thị Swagger UI
- [ ] http://localhost:8000/health trả về `{"status":"healthy"}`

## 🧪 API Testing

### Health Check
```bash
curl http://localhost:8000/health
```
- [ ] Status code: 200
- [ ] Response: `{"status":"healthy"}`

### Quality Grades
```bash
curl http://localhost:8000/api/quality/grades
```
- [ ] Status code: 200
- [ ] Response có 3 grades

### Current Price
```bash
curl -X POST http://localhost:8000/api/pricing/current \
  -H "Content-Type: application/json" \
  -d '{"crop_name":"Cà chua","region":"Hà Nội","quality_grade":"grade_1"}'
```
- [ ] Status code: 200
- [ ] Response có current_price
- [ ] Response có price_trend

### Price Forecast
```bash
curl -X POST http://localhost:8000/api/pricing/forecast \
  -H "Content-Type: application/json" \
  -d '{"crop_name":"Cà chua","region":"Hà Nội","days":7}'
```
- [ ] Status code: 200
- [ ] Response có forecast_data
- [ ] forecast_data có 7 items

## 🖥 Frontend Testing

### Dashboard Page
- [ ] Truy cập http://localhost:5173
- [ ] 4 feature cards hiển thị
- [ ] 3 stat cards hiển thị
- [ ] Click vào cards navigate đúng

### Quality Check Page
- [ ] Truy cập http://localhost:5173/quality
- [ ] Upload area hiển thị
- [ ] Có thể chọn file
- [ ] Preview ảnh hiển thị
- [ ] Button "Kiểm tra chất lượng" hoạt động
- [ ] Kết quả hiển thị sau khi upload
- [ ] Có thể xóa ảnh và upload lại

### Pricing Page
- [ ] Truy cập http://localhost:5173/pricing
- [ ] Form có 4 fields (crop, region, days, button)
- [ ] Dropdown hoạt động
- [ ] Button "Tra cứu" hoạt động
- [ ] 3 stat cards hiển thị kết quả
- [ ] Chart hiển thị đúng
- [ ] Recommendation box hiển thị

## 🗄 Database

### PostgreSQL
```bash
docker-compose exec db psql -U agriuser -d agridb -c "\dt"
```
- [ ] Tables được tạo:
  - [ ] market_prices
  - [ ] price_history
  - [ ] crop_types
  - [ ] harvest_schedules

### Redis
```bash
docker-compose exec redis redis-cli ping
```
- [ ] Response: PONG

## 📊 Performance

- [ ] Frontend load < 3 seconds
- [ ] API response < 1 second
- [ ] Image upload < 5 seconds
- [ ] Chart render smooth

## 🔒 Security

- [ ] .env file không trong git
- [ ] Secrets không hardcoded
- [ ] CORS configured đúng
- [ ] No sensitive data in logs

## 📝 Documentation

- [ ] README.md có đầy đủ thông tin
- [ ] API docs accessible
- [ ] All links work
- [ ] No broken references

## 🛠 Scripts

### setup.sh
```bash
./scripts/setup.sh
```
- [ ] Chạy thành công
- [ ] Tạo .env
- [ ] Tạo directories

### start.sh
```bash
./scripts/start.sh
```
- [ ] Chạy thành công
- [ ] Services start
- [ ] URLs hiển thị

### check_system.sh
```bash
./scripts/check_system.sh
```
- [ ] Chạy thành công
- [ ] All checks pass

### test_api.sh
```bash
./scripts/test_api.sh
```
- [ ] Chạy thành công
- [ ] All tests pass

### demo.sh
```bash
./scripts/demo.sh
```
- [ ] Chạy thành công
- [ ] Demos work

## 🧹 Cleanup

### Stop Services
```bash
docker-compose down
```
- [ ] All containers stopped
- [ ] No errors

### Restart Services
```bash
docker-compose up -d
```
- [ ] All containers restart
- [ ] Services work again

## 📱 Cross-browser Testing

### Desktop
- [ ] Chrome - Works
- [ ] Firefox - Works
- [ ] Safari - Works
- [ ] Edge - Works

### Mobile (Responsive)
- [ ] Mobile view works
- [ ] Touch interactions work
- [ ] Images upload from mobile

## 🎯 Feature Testing

### Quality Check Feature
- [ ] Upload JPG image - Works
- [ ] Upload PNG image - Works
- [ ] Large image (>5MB) - Handled
- [ ] Invalid file type - Error shown
- [ ] Result shows grade
- [ ] Result shows confidence
- [ ] Result shows price range
- [ ] Recommendations shown

### Pricing Feature
- [ ] Select different crops - Works
- [ ] Select different regions - Works
- [ ] Change forecast days - Works
- [ ] Current price displays
- [ ] Trend indicator correct
- [ ] Chart renders
- [ ] Forecast data correct
- [ ] Recommendation shown

## 🐛 Error Handling

### Backend Errors
- [ ] Invalid API request - 400 error
- [ ] Missing fields - Validation error
- [ ] Server error - 500 handled

### Frontend Errors
- [ ] Network error - Error message shown
- [ ] Invalid input - Validation shown
- [ ] Loading states work

## 📈 Monitoring

### Logs
```bash
docker-compose logs -f
```
- [ ] No error logs
- [ ] Request logs visible
- [ ] Timestamps correct

### Resources
```bash
docker stats
```
- [ ] CPU usage reasonable
- [ ] Memory usage reasonable
- [ ] No memory leaks

## ✅ Final Verification

- [ ] All containers running
- [ ] All endpoints working
- [ ] Frontend accessible
- [ ] No console errors
- [ ] No server errors
- [ ] Documentation complete
- [ ] Scripts working
- [ ] Tests passing

## 🎉 Sign Off

**Verified by:** _______________  
**Date:** _______________  
**Version:** 1.0.0  
**Status:** ☐ PASS ☐ FAIL

### Notes:
_______________________________________
_______________________________________
_______________________________________

---

## 📞 If Issues Found

1. Check logs: `docker-compose logs -f`
2. Restart services: `docker-compose restart`
3. Rebuild: `docker-compose up -d --build`
4. Check documentation: [GETTING_STARTED.md](GETTING_STARTED.md)
5. Open issue on GitHub

---

**Tip:** Print this checklist và check từng item khi verify!
