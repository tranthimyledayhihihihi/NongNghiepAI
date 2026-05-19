# TODO - Market Analysis Service

## Step 1: Analysis cache + output spec
- Update `backend/app/services/market_analysis_service.py` to match exact output spec.
- Remove/avoid extra fields from response.
- Ensure evidence items include `source_url`.

## Step 2: Cache behavior
- Implement GET `GET /api/market/analysis` returns cached analysis if valid.
- Implement POST `POST /api/market/analysis/refresh` force refresh asynchronously.
- Add cache TTL logic for analysis results.

## Step 3: No bịa dữ liệu
- Ensure AI/rule parts do not fabricate price/news.
- If data missing (e.g., retail_prices), keep official price and add warning.

## Step 4: Retail crawl policy
- Ensure retail prices are loaded only from `RetailPriceSnapshot` cache via `retail_price_service.get_cached_retail_prices`.
- No retail site crawl per dashboard load.

## Step 5: Quick run/test
- Run import check / minimal call tests for `market_analysis_service.get_analysis`.

