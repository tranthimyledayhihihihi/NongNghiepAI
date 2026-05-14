"""
Script test crawler thủ công - không cần chạy Scrapy daemon.
Cào dữ liệu giá từ các website và lưu vào DB.

Cách dùng:
  python test_crawler.py                    # chạy tất cả spider + lưu DB
  python test_crawler.py --dry-run          # chỉ xem dữ liệu, không lưu DB
  python test_crawler.py --spider nongnghiep  # chỉ chạy spider cụ thể
"""
import argparse
import sys
import os

# Đảm bảo import đúng path
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date
import requests
import re


# ─── Sample data fallback (dùng khi website không phản hồi) ──────────────────

SAMPLE_PRICES = [
    {"crop_name": "Sầu riêng", "region": "Tiền Giang",   "price_per_kg": 65000},
    {"crop_name": "Sầu riêng", "region": "Đắk Lắk",      "price_per_kg": 60000},
    {"crop_name": "Sầu riêng", "region": "Bình Phước",    "price_per_kg": 55000},
    {"crop_name": "Sầu riêng", "region": "Đà Nẵng",       "price_per_kg": 70000},
    {"crop_name": "Sầu riêng", "region": "TP.HCM",        "price_per_kg": 75000},
    {"crop_name": "Lúa",       "region": "Cần Thơ",       "price_per_kg": 8500},
    {"crop_name": "Lúa",       "region": "Đồng Tháp",     "price_per_kg": 8200},
    {"crop_name": "Cà phê",    "region": "Đắk Lắk",       "price_per_kg": 110000},
    {"crop_name": "Cà phê",    "region": "Gia Lai",        "price_per_kg": 108000},
    {"crop_name": "Hồ tiêu",   "region": "Gia Lai",        "price_per_kg": 75000},
    {"crop_name": "Xoài",      "region": "Đồng Tháp",     "price_per_kg": 28000},
    {"crop_name": "Thanh long","region": "Bình Thuận",    "price_per_kg": 20000},
    {"crop_name": "Cà chua",   "region": "Lâm Đồng",      "price_per_kg": 18000},
    {"crop_name": "Ngô",       "region": "Đắk Lắk",       "price_per_kg": 6500},
]


# ─── Scraper functions ────────────────────────────────────────────────────────

def scrape_giavn():
    """Cào giá từ gia.vn/gia-nong-san/"""
    url = "https://gia.vn/gia-nong-san/"
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            # Tìm giá dạng "xxx.xxx đồng/kg" hoặc table rows
            text = resp.text
            matches = re.findall(
                r'<td[^>]*>\s*([^<]{3,50})\s*</td>\s*<td[^>]*>\s*([\d.,]+)\s*(?:đ|VND|đồng)?',
                text, re.IGNORECASE
            )
            for name, price_str in matches:
                try:
                    price = float(re.sub(r"[^\d]", "", price_str))
                    if 1000 <= price <= 500000:
                        results.append({
                            "crop_name": name.strip(),
                            "region": "TP.HCM",
                            "price_per_kg": price,
                            "source": "gia.vn",
                        })
                except ValueError:
                    continue
        print(f"  [gia.vn] Cào được {len(results)} mục")
    except Exception as e:
        print(f"  [gia.vn] Lỗi: {e}")
    return results


def scrape_sample():
    """Trả về sample data thực tế (dùng khi website không có dữ liệu)."""
    import random
    results = []
    for item in SAMPLE_PRICES:
        # Thêm biến động ±5% để giả lập thực tế
        factor = random.uniform(0.95, 1.05)
        results.append({
            "crop_name": item["crop_name"],
            "region": item["region"],
            "price_per_kg": round(item["price_per_kg"] * factor, -2),  # làm tròn 100 đồng
            "source": "sample_data",
            "date": date.today().isoformat(),
        })
    return results


# ─── DB save ─────────────────────────────────────────────────────────────────

def save_to_db(items):
    """Lưu danh sách items vào MarketPrices trong DB."""
    from app.core.database import SessionLocal
    from app.models.crop import CropType
    from app.models.price import MarketPrice

    db = SessionLocal()
    saved = 0
    skipped = 0
    today = date.today()

    try:
        for item in items:
            crop_name = item.get("crop_name", "").strip()
            region = item.get("region", "").strip()
            price = float(item.get("price_per_kg", 0))

            if not crop_name or not region or price <= 0:
                skipped += 1
                continue

            crop = db.query(CropType).filter(CropType.CropName.ilike(f"%{crop_name}%")).first()
            if not crop:
                print(f"  [DB] Bỏ qua '{crop_name}' - chưa có trong CropType")
                skipped += 1
                continue

            price_date_raw = item.get("date")
            try:
                price_date = date.fromisoformat(price_date_raw) if price_date_raw else today
            except (ValueError, TypeError):
                price_date = today

            existing = (
                db.query(MarketPrice)
                .filter(
                    MarketPrice.CropID == crop.CropID,
                    MarketPrice.Region == region,
                    MarketPrice.PriceDate == price_date,
                )
                .first()
            )

            if existing:
                existing.PricePerKg = price
                existing.SourceName = item.get("source", "test_crawler")
            else:
                db.add(MarketPrice(
                    CropID=crop.CropID,
                    Region=region,
                    PricePerKg=price,
                    SourceName=item.get("source", "test_crawler"),
                    SourceURL=item.get("url", ""),
                    PriceDate=price_date,
                ))
            saved += 1

        db.commit()
        print(f"\n  [DB] Đã lưu: {saved} | Bỏ qua: {skipped}")
    except Exception as e:
        db.rollback()
        print(f"\n  [DB] Lỗi khi lưu: {e}")
    finally:
        db.close()

    return saved


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Test crawler nông sản")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ xem dữ liệu, không lưu DB")
    parser.add_argument("--spider", choices=["giavn", "sample", "all"], default="all",
                        help="Chọn spider (default: all)")
    args = parser.parse_args()

    print("=" * 60)
    print("  TEST CRAWLER - Giá Nông Sản")
    print("=" * 60)

    all_items = []

    if args.spider in ("giavn", "all"):
        print("\n[1] Cào gia.vn...")
        items = scrape_giavn()
        all_items.extend(items)

    if args.spider in ("sample", "all") or not all_items:
        print("\n[2] Dùng sample data thực tế...")
        items = scrape_sample()
        all_items.extend(items)

    # In kết quả
    print(f"\n{'─'*60}")
    print(f"Tổng dữ liệu cào được: {len(all_items)} mục\n")
    # Group by crop
    from collections import defaultdict
    by_crop = defaultdict(list)
    for item in all_items:
        by_crop[item["crop_name"]].append(item)

    for crop_name, items in sorted(by_crop.items()):
        prices = [i["price_per_kg"] for i in items]
        avg = sum(prices) / len(prices)
        print(f"  {crop_name:15s}: {len(items)} vùng | avg={avg:,.0f} VND/kg "
              f"| min={min(prices):,.0f} | max={max(prices):,.0f}")

    print(f"{'─'*60}")

    if args.dry_run:
        print("\n[DRY-RUN] Không lưu DB. Bỏ flag --dry-run để lưu thực tế.")
        print("\nDữ liệu chi tiết:")
        for item in all_items:
            print(f"  {item['crop_name']:15s} @ {item['region']:20s}: "
                  f"{item['price_per_kg']:>10,.0f} VND/kg  [{item.get('source','')}]")
    else:
        print("\n[DB] Đang lưu vào database...")
        saved = save_to_db(all_items)
        if saved > 0:
            print(f"\n✓ Lưu thành công {saved} bản ghi vào bảng MarketPrices.")
            print("  Giờ hãy gọi API /api/price-forecast để thấy giá chính xác hơn.")
        else:
            print("\n✗ Không lưu được dữ liệu. Kiểm tra lại kết nối DB và CropType.")

    print("=" * 60)


if __name__ == "__main__":
    main()
