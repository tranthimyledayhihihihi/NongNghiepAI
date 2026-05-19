# Implementation Plan: Pricing Real Data Fix

## Overview

Fix pricing service, dashboard service, API endpoints, and frontend components to use real data from official Vietnamese agriculture sources instead of mock/global commodity data. Remove APIFarmer and Twelve Data from public responses.

## Tasks

- [ ] 1. Fix pricing_service.py - suggest_price và forecast_price
  - [ ] 1.1 Thêm các trường giải thích bắt buộc vào suggest_price response: official_price, quality_coefficient, weather_impact, news_impact, retail_price_diff, suggested_price_range, source_url, cache_status, confidence
  - [ ] 1.2 Sửa forecast_price để dùng lịch sử giá thật từ DB + AI khi có đủ 7 ngày dữ liệu thay vì luôn trả lỗi cứng
  - [ ] 1.3 Đảm bảo compare_regions chỉ dùng dữ liệu từ source_type="official_vietnam_agriculture" hoặc cache thật

- [ ] 2. Fix price_aggregator_service.py - auto-crawl khi cache miss
  - [ ] 2.1 Sửa get_best_current_price: khi cache miss và force_refresh=False, tự động thử crawl thitruongnongsan.gov.vn trước khi trả lỗi
  - [ ] 2.2 Đảm bảo _latest_db_price lọc bỏ bản ghi có source_type="global_commodity" (Stooq/Twelve Data)

- [ ] 3. Fix dashboard_service.py - action-today, price-trend, realtime-status, data-health
  - [ ] 3.1 Sửa get_data_health để hiển thị đúng 6 nguồn theo spec (Open-Meteo, Giá thị trường VN, Tin tức VN, Tavily, Giá bán lẻ, AI, DB cache) - không hiển thị APIFarmer/Twelve Data
  - [ ] 3.2 Sửa realtime-status endpoint trong dashboard.py để trả đúng format nguồn theo spec
  - [ ] 3.3 Sửa action-today để gom context từ Open-Meteo + giá chính thức + tin tức chính thức + Tavily

- [ ] 4. Fix dashboard.py API endpoints
  - [ ] 4.1 Sửa /api/dashboard/realtime-status để trả đúng 7 nguồn theo spec với status: active/cache/partial/error/not_configured
  - [ ] 4.2 Sửa /api/dashboard/news để đảm bảo tin chính thức hiển thị trước Tavily, không hiển thị tin thiếu source_url
  - [ ] 4.3 Sửa /api/dashboard/regional-prices để chỉ dùng MarketPrice có source từ thitruongnongsan.gov.vn

- [ ] 5. Fix pricing.py API endpoints
  - [ ] 5.1 Sửa /api/pricing/history để thử crawl khi DB không có lịch sử
  - [ ] 5.2 Sửa /api/pricing/forecast để dùng AI + lịch sử thật khi có đủ 7 ngày
  - [ ] 5.3 Sửa /api/pricing/suggest để trả đầy đủ các trường giải thích

- [ ] 6. Fix frontend - DataSourceBadge và source display
  - [ ] 6.1 Chuẩn hóa DataSourceBadge component để hiển thị đúng badge: "Nguồn chính thức", "Tavily tổng hợp", "Dữ liệu realtime", "Cache dữ liệu thật", "AI phân tích"
  - [ ] 6.2 Xóa/ẩn hiển thị APIFarmer và Twelve Data khỏi UI
  - [ ] 6.3 Thêm check: nếu is_mock=true hoặc source_url rỗng thì không hiển thị số liệu giá/tin

- [ ] 7. Fix frontend - PricingPage.jsx
  - [ ] 7.1 Hiển thị đầy đủ các trường giải thích từ suggest response: quality_coefficient, weather_impact, news_impact, retail_price_diff, suggested_price_range
  - [ ] 7.2 Khi cache_status="miss" hiển thị đúng error state với nút "Thử lại"
  - [ ] 7.3 Khi cache_status="stale_cache" hiển thị cảnh báo "Dữ liệu thực tế gần nhất - cần cập nhật"

- [ ] 8. Fix frontend - Dashboard.jsx
  - [ ] 8.1 Thêm check is_mock cho featured_crop và regional_prices - không render số liệu giả
  - [ ] 8.2 Cải thiện error handling: mỗi card có loading/error state riêng
  - [ ] 8.3 Cập nhật STATUS_NAME_LABELS để hiển thị đúng 7 nguồn theo spec

- [ ] 9. Fix frontend - MarketPage.jsx và news display
  - [ ] 9.1 Thêm badge "Nguồn chính thức" cho tin từ thitruongnongsan.gov.vn
  - [ ] 9.2 Thêm badge "Tavily tổng hợp" cho tin từ Tavily
  - [ ] 9.3 Không hiển thị tin thiếu source_url

- [ ] 10. Tạo test script kiểm tra toàn bộ spec
  - [ ] 10.1 Tạo backend/tests/test_real_data_spec.py với các test case theo spec
  - [ ] 10.2 Tạo test_postman_collection.json hoặc test script bash/python để test các endpoint
  - [ ] 10.3 Chạy search toàn project để kiểm tra không còn mock/APIFarmer/TwelveData trong public response

## Task Dependency Graph

```json
{
  "waves": [
    { "wave": 1, "tasks": ["1"] },
    { "wave": 2, "tasks": ["2"] },
    { "wave": 3, "tasks": ["3"] },
    { "wave": 4, "tasks": ["4", "5"] },
    { "wave": 5, "tasks": ["6", "7", "8", "9"] },
    { "wave": 6, "tasks": ["10"] }
  ]
}
```

Tasks 1-5 are backend fixes. Tasks 6-9 are frontend fixes that can run in parallel after backend tasks. Task 10 validates everything.

## Notes

- All price data must come from source_type="official_vietnam_agriculture" or real cache
- Never expose mock data, APIFarmer, or Twelve Data (Stooq) in public API responses
- Frontend must check is_mock flag and source_url before rendering price/news data
- Official source: thitruongnongsan.gov.vn
