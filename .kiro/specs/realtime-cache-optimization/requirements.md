# Requirements Document

## Introduction

Hệ thống NongNghiepAI hiện tại gọi nhiều nguồn dữ liệu realtime (Open-Meteo, thitruongnongsan.gov.vn, Tavily, v.v.) trực tiếp khi user mở trang, dẫn đến nguy cơ timeout, chậm tải và trải nghiệm kém. Feature này tối ưu hóa kiến trúc bằng cách tách biệt hoàn toàn luồng **đọc nhanh từ DB cache** và luồng **background refresh định kỳ**, đảm bảo:

- Frontend luôn đọc nhanh từ DB cache thật (không mock).
- Background scheduler/worker cập nhật dữ liệu định kỳ theo TTL từng loại.
- Mọi response public đều có đầy đủ metadata chuẩn: `source_name`, `source_url`, `is_realtime`, `is_mock=false`, `cache_status`, `fetched_at`, `last_updated`, `data_age_minutes`.
- Nếu cache miss và realtime lỗi → trả `error_response` với `cache_status="miss"`, không mock.

## Glossary

- **Cache_DB**: Dữ liệu thật đã được lấy từ nguồn thực tế và lưu vào database. Không phải mock. Có đầy đủ `source_url`, `source_name`, `fetched_at`, `is_mock=false`.
- **Background_Scheduler**: Tiến trình chạy nền định kỳ (APScheduler hoặc tương đương) để gọi API/crawl và cập nhật Cache_DB.
- **Cache_Status**: Trạng thái cache của dữ liệu trả về. Một trong 5 giá trị: `live`, `fresh_cache`, `stale_cache`, `miss`, `error`.
- **TTL**: Time-To-Live — thời gian tối đa một bản ghi cache được coi là "fresh". Sau TTL là `stale_cache`, sau Stale_TTL là `miss`.
- **Stale_TTL**: Thời gian tối đa một bản ghi cache được coi là "stale" (vẫn dùng được nhưng cần refresh). Sau Stale_TTL là `miss`.
- **Circuit_Breaker**: Cơ chế ngắt mạch — sau N lần lỗi liên tiếp từ một nguồn, tạm thời không gọi nguồn đó trong khoảng thời gian cooldown.
- **API_Response**: Cấu trúc JSON chuẩn trả về từ mọi endpoint public, bao gồm đầy đủ metadata bắt buộc.
- **External_Source**: Nguồn dữ liệu bên ngoài (Open-Meteo, thitruongnongsan.gov.vn, Tavily, v.v.).
- **Dashboard**: Trang tổng quan của ứng dụng, tổng hợp dữ liệu thời tiết, giá nông sản, tin tức thị trường.
- **Retry**: Cơ chế thử lại request khi gặp lỗi tạm thời, tối đa 1-2 lần.
- **Ingestion_Log**: Bản ghi lịch sử mỗi lần Background_Scheduler chạy, lưu trạng thái, số bản ghi, lỗi nếu có.

---

## Requirements

### Requirement 1: Background Scheduler — Không gọi realtime khi user mở trang

**User Story:** As a system architect, I want background data refresh to be completely decoupled from user requests, so that the web application never blocks or times out waiting for external API calls.

#### Acceptance Criteria

1. THE Background_Scheduler SHALL fetch data from all External_Sources independently of user HTTP requests.
2. WHEN a user opens the Dashboard, THE System SHALL read data exclusively from Cache_DB without initiating any External_Source calls.
3. THE Background_Scheduler SHALL run on a configurable schedule for each data type according to the TTL defined in Requirement 2.
4. WHEN the Background_Scheduler starts, THE System SHALL log an Ingestion_Log entry with `status="running"`, `source_name`, and `started_at`.
5. WHEN the Background_Scheduler completes a fetch cycle, THE System SHALL update the Ingestion_Log entry with `status="success"`, `records_fetched`, `records_saved`, and `finished_at`.
6. IF the Background_Scheduler encounters an error during a fetch cycle, THEN THE System SHALL update the Ingestion_Log entry with `status="failed"` and `error_message`, without crashing the scheduler process.
7. THE Background_Scheduler SHALL support at least the following data types: weather_current, weather_hourly, weather_forecast, official_price, market_news, tavily_news, retail_price, market_analysis.

---

### Requirement 2: TTL Configuration — Thời gian sống của cache theo từng loại dữ liệu

**User Story:** As a developer, I want each data type to have a configurable TTL, so that I can balance data freshness against API call frequency.

#### Acceptance Criteria

1. THE System SHALL enforce the following default TTL values for Cache_DB freshness:
   - `weather_current`: 15–30 phút (default 30 phút)
   - `weather_hourly`: 30 phút
   - `weather_forecast` (7 ngày): 60–180 phút (default 180 phút)
   - `official_price` (giá nông sản chính thức): 60–180 phút (default 180 phút)
   - `market_news` (tin tức thị trường): 60–120 phút (default 120 phút)
   - `tavily_news`: 60–120 phút (default 120 phút)
   - `retail_price` (giá bán lẻ tham khảo): 180–360 phút (default 360 phút)
   - `market_analysis`: 30–60 phút (default 60 phút)
2. THE System SHALL expose all TTL values as configurable settings (environment variables or config file) without requiring code changes.
3. WHEN a Cache_DB record's age exceeds its TTL but is within its Stale_TTL, THE System SHALL return the record with `cache_status="stale_cache"` and a warning message.
4. WHEN a Cache_DB record's age exceeds its Stale_TTL, THE System SHALL return `cache_status="miss"` and not return stale data.
5. THE System SHALL use the following Stale_TTL multipliers as defaults: weather_current 6×TTL, weather_hourly 4×TTL, weather_forecast 4×TTL, official_price 8×TTL, market_news 12×TTL, retail_price 4×TTL, market_analysis 4×TTL.

---

### Requirement 3: Cache_Status chuẩn — Trạng thái cache trong mọi response

**User Story:** As a frontend developer, I want every API response to include a standardized `cache_status` field, so that I can display appropriate data freshness indicators to users.

#### Acceptance Criteria

1. THE System SHALL include `cache_status` in every public API response with exactly one of the following values: `live`, `fresh_cache`, `stale_cache`, `miss`, `error`.
2. WHEN data is fetched live from an External_Source in the same request cycle, THE System SHALL set `cache_status="live"`.
3. WHEN data is read from Cache_DB and its age is within TTL, THE System SHALL set `cache_status="fresh_cache"`.
4. WHEN data is read from Cache_DB and its age is between TTL and Stale_TTL, THE System SHALL set `cache_status="stale_cache"`.
5. WHEN no valid Cache_DB record exists and External_Source is unavailable, THE System SHALL set `cache_status="miss"`.
6. WHEN an External_Source returns an error during a background refresh, THE System SHALL set `cache_status="error"` in the Ingestion_Log.
7. THE System SHALL never return `cache_status` values outside the defined set of 5 values.

---

### Requirement 4: Metadata bắt buộc trong mọi response public

**User Story:** As a frontend developer, I want every public API response to include complete data provenance metadata, so that users can verify data sources and freshness.

#### Acceptance Criteria

1. THE System SHALL include the following fields in every public API response:
   - `source_name`: tên nguồn dữ liệu (string, không null)
   - `source_url`: URL nguồn dữ liệu (string hoặc null nếu không có)
   - `is_realtime`: boolean — true chỉ khi dữ liệu được lấy live trong request hiện tại
   - `is_mock`: boolean — luôn là `false`
   - `cache_status`: một trong 5 giá trị chuẩn (xem Requirement 3)
   - `fetched_at`: ISO 8601 datetime khi dữ liệu được lấy từ nguồn
   - `last_updated`: ISO 8601 datetime lần cập nhật gần nhất
   - `data_age_minutes`: số nguyên không âm — tuổi dữ liệu tính bằng phút
2. THE System SHALL set `is_mock=false` in all public API responses regardless of data source.
3. WHEN `cache_status="miss"` or `cache_status="error"`, THE System SHALL set `is_realtime=false` and `data_age_minutes=null`.
4. THE Cache_DB SHALL store `source_url`, `source_name`, `fetched_at`, and `is_mock=false` for every real data record.
5. THE System SHALL compute `data_age_minutes` as the integer number of minutes elapsed since `fetched_at`.

---

### Requirement 5: Timeout ngắn và Retry cho External_Source

**User Story:** As a system operator, I want external API calls to have short timeouts and limited retries, so that a slow external source does not block background workers or degrade system performance.

#### Acceptance Criteria

1. THE System SHALL apply a connect timeout of at most 3 seconds for all External_Source requests.
2. THE System SHALL apply a read timeout of at most 8 seconds for weather External_Source requests.
3. THE System SHALL apply a read timeout of at most 10 seconds for market data External_Source requests.
4. THE System SHALL apply a total timeout of at most 12 seconds for any single External_Source request.
5. THE System SHALL retry a failed External_Source request at most 2 times before marking the request as failed.
6. WHEN retrying, THE System SHALL apply exponential backoff with a base delay of 0.4 seconds between attempts.
7. IF an External_Source request fails after all retries, THEN THE System SHALL log the failure with `service_name`, `url`, `attempt_count`, and `error_message`.

---

### Requirement 6: Circuit Breaker — Ngắt mạch khi nguồn lỗi liên tục

**User Story:** As a system operator, I want a circuit breaker to prevent repeated calls to a failing external source, so that the system remains stable when an external dependency is unavailable.

#### Acceptance Criteria

1. THE Circuit_Breaker SHALL track failure counts per External_Source key (e.g., `open_meteo_forecast`, `thitruongnongsan_price`, `tavily_news`).
2. WHEN an External_Source accumulates 3 or more consecutive failures, THE Circuit_Breaker SHALL open the circuit and block further calls to that source for a configurable cooldown period (default 600 seconds).
3. WHILE the Circuit_Breaker is open for an External_Source, THE System SHALL return `cache_status="error"` with an appropriate error message without attempting to call the External_Source.
4. WHEN the cooldown period expires, THE Circuit_Breaker SHALL allow one probe request to the External_Source.
5. IF the probe request succeeds, THEN THE Circuit_Breaker SHALL reset the failure count and close the circuit.
6. IF the probe request fails, THEN THE Circuit_Breaker SHALL extend the cooldown period and remain open.
7. THE Circuit_Breaker SHALL expose a status endpoint returning the current state (`active`, `error`, `cache`) for each tracked External_Source.

---

### Requirement 7: Isolation — Một nguồn lỗi không làm crash toàn Dashboard

**User Story:** As a user, I want the dashboard to remain functional even when one data source fails, so that I can still access available information without the entire page crashing.

#### Acceptance Criteria

1. THE Dashboard SHALL load successfully even when one or more External_Sources are unavailable.
2. WHEN a data module (weather, prices, news, market_analysis) fails to load, THE Dashboard SHALL display the remaining modules with their available data.
3. THE System SHALL wrap each dashboard data module call in an independent error boundary that catches exceptions without propagating them to other modules.
4. WHEN a module fails, THE System SHALL include a `module_status` entry in the dashboard response with `{"module": "<name>", "ok": false, "error": "<message>", "fallback_used": true}`.
5. THE System SHALL never return an HTTP 500 error for the dashboard summary endpoint due to a single module failure.
6. WHEN all data modules fail simultaneously, THE System SHALL return an empty dashboard structure with `cache_status="miss"` and `module_status` entries for all failed modules.

---

### Requirement 8: Cache Miss và Error Response — Không mock khi thiếu dữ liệu

**User Story:** As a frontend developer, I want the API to return a clear error response when data is unavailable, so that I can display an appropriate message to users instead of showing incorrect mock data.

#### Acceptance Criteria

1. WHEN Cache_DB has no valid record for a requested data type and External_Source is unavailable, THE System SHALL return an error response with `cache_status="miss"` and `is_mock=false`.
2. THE System SHALL never generate synthetic, mock, or placeholder data to fill a cache miss.
3. WHEN returning a cache miss error, THE System SHALL include `error_code`, `error_message`, `source_name`, `source_url`, `cache_status="miss"`, `is_mock=false`, `is_realtime=false`.
4. IF a cache miss error response is returned, THEN THE System SHALL include a human-readable `error_message` in Vietnamese explaining why data is unavailable.
5. THE System SHALL distinguish between `cache_status="miss"` (no data available) and `cache_status="stale_cache"` (data available but outdated).
6. WHEN `cache_status="stale_cache"`, THE System SHALL include a `warning` field with a Vietnamese message indicating the data is outdated.

---

### Requirement 9: Background Refresh API — Endpoint kích hoạt refresh thủ công

**User Story:** As an administrator, I want to manually trigger a background data refresh for specific data types, so that I can force-update the cache without waiting for the scheduled interval.

#### Acceptance Criteria

1. THE System SHALL provide a POST endpoint `/api/dashboard/refresh` that accepts `source` parameter (values: `weather`, `prices`, `news`, `all`) to trigger a background refresh.
2. WHEN a refresh is triggered, THE System SHALL return immediately with `cache_status="processing"` without waiting for the refresh to complete.
3. THE System SHALL execute the refresh in a background thread/task to avoid blocking the HTTP response.
4. WHEN a refresh for the same source is already in progress, THE System SHALL return `cache_status="processing"` with an appropriate message instead of starting a duplicate refresh.
5. WHEN a manual refresh completes successfully, THE System SHALL update the Cache_DB records and the Ingestion_Log.
6. IF a manual refresh fails, THEN THE System SHALL log the failure in the Ingestion_Log with `status="failed"` and `error_message`.

---

### Requirement 10: Parser và Serializer cho Cache_DB — Round-trip integrity

**User Story:** As a developer, I want all data stored in and retrieved from Cache_DB to maintain structural integrity through serialization and deserialization, so that no data corruption occurs during cache operations.

#### Acceptance Criteria

1. THE Cache_DB_Serializer SHALL serialize all datetime fields to ISO 8601 format before storage.
2. THE Cache_DB_Deserializer SHALL deserialize ISO 8601 datetime strings back to datetime objects upon retrieval.
3. FOR ALL valid Cache_DB records, serializing then deserializing SHALL produce an equivalent record (round-trip property).
4. THE Cache_DB_Serializer SHALL serialize `is_mock` as boolean `false` for all real data records.
5. WHEN deserializing a Cache_DB record with `is_mock=true`, THE System SHALL reject the record and log a warning.
6. THE Cache_DB_Serializer SHALL serialize `cache_status` using only the 5 valid values defined in Requirement 3.
7. WHEN deserializing a `cache_status` value not in the valid set, THE Cache_DB_Deserializer SHALL normalize it to `"miss"` as the default.

---

### Requirement 11: Data Health Monitoring — Giám sát sức khỏe dữ liệu

**User Story:** As a system operator, I want a data health endpoint that shows the status of all data sources and cache freshness, so that I can quickly identify which sources are stale or failing.

#### Acceptance Criteria

1. THE System SHALL provide a GET endpoint `/api/dashboard/data-health` returning the health status of all data sources.
2. THE Data_Health_Response SHALL include for each source: `name`, `status` (one of: `active`, `stale`, `error`, `empty`), `role`, `source_url`, `last_fetched_at`, `data_age_minutes`, `record_count`.
3. WHEN a data source has records with `fetched_at` within TTL, THE System SHALL report `status="active"` for that source.
4. WHEN a data source has records with `fetched_at` between TTL and Stale_TTL, THE System SHALL report `status="stale"` for that source.
5. WHEN a data source has no records or all records exceed Stale_TTL, THE System SHALL report `status="empty"` for that source.
6. WHEN the Circuit_Breaker is open for a data source, THE System SHALL report `status="error"` for that source.
7. THE Data_Health_Response SHALL include an overall `health_score` (0–100) computed from the proportion of active sources weighted by their importance.
