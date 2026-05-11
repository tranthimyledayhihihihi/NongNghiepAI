"""
Seed dữ liệu ban đầu cho bảng CropTypes.
Chạy một lần: python seed_db.py
Hoặc tự động được gọi khi server khởi động.
"""
from app.core.database import SessionLocal
from app.models.crop import CropType


# Category hợp lệ theo CHECK constraint: 'Lua gao','Trai cay','Rau cu','Cong nghiep','Khac'
CROPS_DATA = [
    # ── Ngũ cốc ──────────────────────────────────────────────────────────────
    {
        "CropName": "Lúa",        "CropNameEN": "Rice",
        "Category": "Lua gao",    "GrowthDurationDays": 105,
        "HarvestSeason": "Tháng 3-4, 8-9",
        "TypicalPriceMin": 6000,  "TypicalPriceMax": 12000,
        "Description": "Lúa nước IR50404, Jasmine, OM5451 — cây lương thực chính Việt Nam",
    },
    {
        "CropName": "Ngô",        "CropNameEN": "Corn",
        "Category": "Lua gao",    "GrowthDurationDays": 90,
        "HarvestSeason": "Tháng 1-2, 6-7",
        "TypicalPriceMin": 4000,  "TypicalPriceMax": 9000,
        "Description": "Ngô lai NK66, CP888 — làm thức ăn chăn nuôi và thực phẩm",
    },
    {
        "CropName": "Đậu tương",  "CropNameEN": "Soybean",
        "Category": "Lua gao",    "GrowthDurationDays": 95,
        "HarvestSeason": "Tháng 2-3, 7-8",
        "TypicalPriceMin": 12000, "TypicalPriceMax": 22000,
        "Description": "Đậu tương DT84, DT96 — nguyên liệu dầu thực vật và thức ăn chăn nuôi",
    },
    {
        "CropName": "Đậu phộng",  "CropNameEN": "Peanut",
        "Category": "Lua gao",    "GrowthDurationDays": 120,
        "HarvestSeason": "Tháng 2-3, 7-8",
        "TypicalPriceMin": 20000, "TypicalPriceMax": 40000,
        "Description": "Lạc (đậu phộng) L14, L23 — xuất khẩu và chế biến dầu",
    },
    # ── Rau củ ngắn ngày ──────────────────────────────────────────────────────
    {
        "CropName": "Cà chua",    "CropNameEN": "Tomato",
        "Category": "Rau cu",     "GrowthDurationDays": 75,
        "HarvestSeason": "Quanh năm (chính vụ tháng 11-3)",
        "TypicalPriceMin": 5000,  "TypicalPriceMax": 40000,
        "Description": "Cà chua bi, cà chua thân gỗ, cherry tomato",
    },
    {
        "CropName": "Rau muống",  "CropNameEN": "Water Spinach",
        "Category": "Rau cu",     "GrowthDurationDays": 30,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 4000,  "TypicalPriceMax": 18000,
        "Description": "Rau muống nước và rau muống cạn",
    },
    {
        "CropName": "Khoai lang", "CropNameEN": "Sweet Potato",
        "Category": "Rau cu",     "GrowthDurationDays": 100,
        "HarvestSeason": "Tháng 10-1",
        "TypicalPriceMin": 6000,  "TypicalPriceMax": 30000,
        "Description": "Khoai lang tím Nhật, khoai lang mật, khoai lang vàng",
    },
    {
        "CropName": "Rau cải",    "CropNameEN": "Mustard Green",
        "Category": "Rau cu",     "GrowthDurationDays": 35,
        "HarvestSeason": "Quanh năm (chính vụ tháng 10-3)",
        "TypicalPriceMin": 4000,  "TypicalPriceMax": 30000,
        "Description": "Cải xanh, cải ngọt, cải thìa, pak choi",
    },
    {
        "CropName": "Cải bắp",    "CropNameEN": "Cabbage",
        "Category": "Rau cu",     "GrowthDurationDays": 70,
        "HarvestSeason": "Tháng 10-3",
        "TypicalPriceMin": 3000,  "TypicalPriceMax": 20000,
        "Description": "Bắp cải xanh, bắp cải tím Đà Lạt",
    },
    {
        "CropName": "Cải thảo",   "CropNameEN": "Chinese Cabbage",
        "Category": "Rau cu",     "GrowthDurationDays": 65,
        "HarvestSeason": "Tháng 10-3",
        "TypicalPriceMin": 4000,  "TypicalPriceMax": 25000,
        "Description": "Cải thảo Đà Lạt, cải thảo Hà Nội",
    },
    {
        "CropName": "Xà lách",    "CropNameEN": "Lettuce",
        "Category": "Rau cu",     "GrowthDurationDays": 40,
        "HarvestSeason": "Quanh năm (chính vụ tháng 10-3)",
        "TypicalPriceMin": 6000,  "TypicalPriceMax": 50000,
        "Description": "Xà lách xoăn, xà lách romaine, salad",
    },
    {
        "CropName": "Hành lá",    "CropNameEN": "Spring Onion",
        "Category": "Rau cu",     "GrowthDurationDays": 35,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 8000,  "TypicalPriceMax": 60000,
        "Description": "Hành lá (hành xanh), gia vị phổ biến",
    },
    {
        "CropName": "Hành tây",   "CropNameEN": "Onion",
        "Category": "Rau cu",     "GrowthDurationDays": 60,
        "HarvestSeason": "Tháng 1-3",
        "TypicalPriceMin": 5000,  "TypicalPriceMax": 40000,
        "Description": "Hành tây vàng, hành tây đỏ Đà Lạt",
    },
    {
        "CropName": "Tỏi",        "CropNameEN": "Garlic",
        "Category": "Rau cu",     "GrowthDurationDays": 90,
        "HarvestSeason": "Tháng 3-4",
        "TypicalPriceMin": 20000, "TypicalPriceMax": 120000,
        "Description": "Tỏi Lý Sơn, tỏi Khánh Hòa — gia vị thiết yếu",
    },
    {
        "CropName": "Gừng",       "CropNameEN": "Ginger",
        "Category": "Rau cu",     "GrowthDurationDays": 240,
        "HarvestSeason": "Tháng 11-1",
        "TypicalPriceMin": 12000, "TypicalPriceMax": 80000,
        "Description": "Gừng trâu, gừng dé — gia vị và dược liệu",
    },
    {
        "CropName": "Nghệ",       "CropNameEN": "Turmeric",
        "Category": "Rau cu",     "GrowthDurationDays": 270,
        "HarvestSeason": "Tháng 11-1",
        "TypicalPriceMin": 10000, "TypicalPriceMax": 60000,
        "Description": "Nghệ vàng, nghệ đen — gia vị và dược liệu",
    },
    {
        "CropName": "Cà rốt",     "CropNameEN": "Carrot",
        "Category": "Rau cu",     "GrowthDurationDays": 100,
        "HarvestSeason": "Tháng 10-2",
        "TypicalPriceMin": 5000,  "TypicalPriceMax": 35000,
        "Description": "Cà rốt Đà Lạt, Hải Dương — giàu beta-carotene",
    },
    {
        "CropName": "Khoai tây",  "CropNameEN": "Potato",
        "Category": "Rau cu",     "GrowthDurationDays": 90,
        "HarvestSeason": "Tháng 11-2",
        "TypicalPriceMin": 8000,  "TypicalPriceMax": 35000,
        "Description": "Khoai tây Đà Lạt, khoai tây Atlantic",
    },
    {
        "CropName": "Su hào",     "CropNameEN": "Kohlrabi",
        "Category": "Rau cu",     "GrowthDurationDays": 65,
        "HarvestSeason": "Tháng 10-3",
        "TypicalPriceMin": 3000,  "TypicalPriceMax": 20000,
        "Description": "Su hào xanh, su hào tím Đà Lạt",
    },
    {
        "CropName": "Củ cải",     "CropNameEN": "Radish",
        "Category": "Rau cu",     "GrowthDurationDays": 70,
        "HarvestSeason": "Tháng 10-2",
        "TypicalPriceMin": 4000,  "TypicalPriceMax": 25000,
        "Description": "Củ cải trắng (daikon), củ cải đỏ",
    },
    {
        "CropName": "Bí đỏ",      "CropNameEN": "Pumpkin",
        "Category": "Rau cu",     "GrowthDurationDays": 80,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 4000,  "TypicalPriceMax": 30000,
        "Description": "Bí đỏ, bí ngô — giàu vitamin A",
    },
    {
        "CropName": "Bí xanh",    "CropNameEN": "Winter Melon",
        "Category": "Rau cu",     "GrowthDurationDays": 80,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 3000,  "TypicalPriceMax": 20000,
        "Description": "Bí xanh (bí đao), dùng nấu canh và chế biến",
    },
    {
        "CropName": "Bầu",        "CropNameEN": "Bottle Gourd",
        "Category": "Rau cu",     "GrowthDurationDays": 75,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 3000,  "TypicalPriceMax": 22000,
        "Description": "Bầu trắng, bầu sao — thực phẩm phổ biến miền Nam",
    },
    {
        "CropName": "Mướp",       "CropNameEN": "Luffa",
        "Category": "Rau cu",     "GrowthDurationDays": 70,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 4000,  "TypicalPriceMax": 28000,
        "Description": "Mướp hương, mướp khía (mướp gai)",
    },
    {
        "CropName": "Khổ qua",    "CropNameEN": "Bitter Melon",
        "Category": "Rau cu",     "GrowthDurationDays": 70,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 6000,  "TypicalPriceMax": 50000,
        "Description": "Khổ qua (mướp đắng) — thực phẩm và dược liệu",
    },
    {
        "CropName": "Đậu cove",   "CropNameEN": "French Bean",
        "Category": "Rau cu",     "GrowthDurationDays": 65,
        "HarvestSeason": "Tháng 10-4",
        "TypicalPriceMin": 8000,  "TypicalPriceMax": 50000,
        "Description": "Đậu que, đậu cove Đà Lạt",
    },
    {
        "CropName": "Đậu đũa",    "CropNameEN": "Yard-long Bean",
        "Category": "Rau cu",     "GrowthDurationDays": 65,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 6000,  "TypicalPriceMax": 40000,
        "Description": "Đậu đũa xanh, đậu đũa tím",
    },
    {
        "CropName": "Ớt",         "CropNameEN": "Chili",
        "Category": "Rau cu",     "GrowthDurationDays": 90,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 10000, "TypicalPriceMax": 120000,
        "Description": "Ớt sừng, ớt chỉ thiên, ớt chuông — gia vị và chế biến",
    },
    {
        "CropName": "Mồng tơi",   "CropNameEN": "Malabar Spinach",
        "Category": "Rau cu",     "GrowthDurationDays": 35,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 4000,  "TypicalPriceMax": 22000,
        "Description": "Rau mồng tơi — rau ăn lá phổ biến mùa hè",
    },
    {
        "CropName": "Rau cần",    "CropNameEN": "Celery",
        "Category": "Rau cu",     "GrowthDurationDays": 70,
        "HarvestSeason": "Tháng 10-3",
        "TypicalPriceMin": 8000,  "TypicalPriceMax": 50000,
        "Description": "Rau cần ta, cần tây — gia vị và rau ăn",
    },
    {
        "CropName": "Ngó sen",    "CropNameEN": "Lotus Root",
        "Category": "Rau cu",     "GrowthDurationDays": 120,
        "HarvestSeason": "Tháng 10-2",
        "TypicalPriceMin": 20000, "TypicalPriceMax": 80000,
        "Description": "Ngó sen Đồng Tháp, Cần Thơ — đặc sản Đồng bằng sông Cửu Long",
    },
    # ── Cây ăn quả ────────────────────────────────────────────────────────────
    {
        "CropName": "Sầu riêng",  "CropNameEN": "Durian",
        "Category": "Trai cay",   "GrowthDurationDays": 1460,
        "HarvestSeason": "Tháng 5-8 (chính vụ)",
        "TypicalPriceMin": 35000, "TypicalPriceMax": 200000,
        "Description": "Musang King, Ri6, Monthong — vua trái cây, xuất khẩu Trung Quốc",
    },
    {
        "CropName": "Xoài",       "CropNameEN": "Mango",
        "Category": "Trai cay",   "GrowthDurationDays": 1095,
        "HarvestSeason": "Tháng 3-6",
        "TypicalPriceMin": 8000,  "TypicalPriceMax": 80000,
        "Description": "Xoài cát Hòa Lộc, xoài Đài Loan, xoài GL6",
    },
    {
        "CropName": "Thanh long", "CropNameEN": "Dragon Fruit",
        "Category": "Trai cay",   "GrowthDurationDays": 540,
        "HarvestSeason": "Quanh năm (chính vụ tháng 5-9)",
        "TypicalPriceMin": 5000,  "TypicalPriceMax": 60000,
        "Description": "Thanh long ruột đỏ, ruột trắng Bình Thuận, Long An",
    },
    {
        "CropName": "Chuối",      "CropNameEN": "Banana",
        "Category": "Trai cay",   "GrowthDurationDays": 365,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 4000,  "TypicalPriceMax": 30000,
        "Description": "Chuối già hương, chuối tiêu, chuối nam mỹ",
    },
    {
        "CropName": "Dứa",        "CropNameEN": "Pineapple",
        "Category": "Trai cay",   "GrowthDurationDays": 365,
        "HarvestSeason": "Tháng 3-8",
        "TypicalPriceMin": 4000,  "TypicalPriceMax": 20000,
        "Description": "Dứa Queen, dứa Cayenne — Tiền Giang, Long An",
    },
    {
        "CropName": "Dưa hấu",   "CropNameEN": "Watermelon",
        "Category": "Trai cay",   "GrowthDurationDays": 80,
        "HarvestSeason": "Tháng 1-4",
        "TypicalPriceMin": 3000,  "TypicalPriceMax": 25000,
        "Description": "Dưa hấu ruột đỏ, dưa hấu không hạt",
    },
    {
        "CropName": "Bơ",         "CropNameEN": "Avocado",
        "Category": "Trai cay",   "GrowthDurationDays": 1460,
        "HarvestSeason": "Tháng 8-12",
        "TypicalPriceMin": 15000, "TypicalPriceMax": 100000,
        "Description": "Bơ Booth, bơ 034, bơ Reed — Đắk Lắk, Lâm Đồng",
    },
    {
        "CropName": "Mít",        "CropNameEN": "Jackfruit",
        "Category": "Trai cay",   "GrowthDurationDays": 1460,
        "HarvestSeason": "Tháng 3-7",
        "TypicalPriceMin": 6000,  "TypicalPriceMax": 60000,
        "Description": "Mít thái (siêu sớm), mít tố nữ",
    },
    {
        "CropName": "Nhãn",       "CropNameEN": "Longan",
        "Category": "Trai cay",   "GrowthDurationDays": 730,
        "HarvestSeason": "Tháng 7-9",
        "TypicalPriceMin": 12000, "TypicalPriceMax": 80000,
        "Description": "Nhãn lồng Hưng Yên, nhãn da bò, nhãn tiêu da bò",
    },
    {
        "CropName": "Vải",        "CropNameEN": "Lychee",
        "Category": "Trai cay",   "GrowthDurationDays": 730,
        "HarvestSeason": "Tháng 5-7",
        "TypicalPriceMin": 12000, "TypicalPriceMax": 80000,
        "Description": "Vải thiều Bắc Giang, Hải Dương",
    },
    {
        "CropName": "Cam",        "CropNameEN": "Orange",
        "Category": "Trai cay",   "GrowthDurationDays": 730,
        "HarvestSeason": "Tháng 10-2",
        "TypicalPriceMin": 10000, "TypicalPriceMax": 60000,
        "Description": "Cam sành Hà Giang, Nghệ An, Vĩnh Long",
    },
    {
        "CropName": "Bưởi",       "CropNameEN": "Pomelo",
        "Category": "Trai cay",   "GrowthDurationDays": 1095,
        "HarvestSeason": "Tháng 9-12",
        "TypicalPriceMin": 8000,  "TypicalPriceMax": 60000,
        "Description": "Bưởi da xanh, bưởi năm roi, bưởi Diễn",
    },
    {
        "CropName": "Ổi",         "CropNameEN": "Guava",
        "Category": "Trai cay",   "GrowthDurationDays": 365,
        "HarvestSeason": "Quanh năm",
        "TypicalPriceMin": 6000,  "TypicalPriceMax": 40000,
        "Description": "Ổi lê, ổi không hạt — Bình Dương, Tiền Giang",
    },
    # ── Cây công nghiệp ───────────────────────────────────────────────────────
    {
        "CropName": "Cà phê",     "CropNameEN": "Coffee",
        "Category": "Cong nghiep","GrowthDurationDays": 1095,
        "HarvestSeason": "Tháng 11-1",
        "TypicalPriceMin": 60000, "TypicalPriceMax": 200000,
        "Description": "Robusta (Đắk Lắk, Gia Lai), Arabica (Lâm Đồng, Kon Tum)",
    },
    {
        "CropName": "Hồ tiêu",   "CropNameEN": "Black Pepper",
        "Category": "Cong nghiep","GrowthDurationDays": 1095,
        "HarvestSeason": "Tháng 1-3",
        "TypicalPriceMin": 40000, "TypicalPriceMax": 180000,
        "Description": "Tiêu đen, tiêu sọ — Bình Phước, Gia Lai, Đắk Nông",
    },
    {
        "CropName": "Điều",       "CropNameEN": "Cashew",
        "Category": "Cong nghiep","GrowthDurationDays": 1460,
        "HarvestSeason": "Tháng 2-5",
        "TypicalPriceMin": 25000, "TypicalPriceMax": 100000,
        "Description": "Điều nhân W240, W320 — Bình Phước, Đồng Nai, Đắk Lắk",
    },
    {
        "CropName": "Mía",        "CropNameEN": "Sugarcane",
        "Category": "Cong nghiep","GrowthDurationDays": 365,
        "HarvestSeason": "Tháng 11-4",
        "TypicalPriceMin": 700,   "TypicalPriceMax": 2500,
        "Description": "Mía nguyên liệu cho nhà máy đường — Long An, Tây Ninh",
    },
    {
        "CropName": "Chè",        "CropNameEN": "Tea",
        "Category": "Cong nghiep","GrowthDurationDays": 1095,
        "HarvestSeason": "Quanh năm (hái búp)",
        "TypicalPriceMin": 5000,  "TypicalPriceMax": 30000,
        "Description": "Chè xanh, chè đen, chè ô long — Thái Nguyên, Lâm Đồng",
    },
    {
        "CropName": "Cao su",     "CropNameEN": "Rubber",
        "Category": "Cong nghiep","GrowthDurationDays": 2555,
        "HarvestSeason": "Quanh năm (cạo mủ)",
        "TypicalPriceMin": 25000, "TypicalPriceMax": 60000,
        "Description": "Cao su thiên nhiên — Bình Dương, Đồng Nai, Bình Phước",
    },
    {
        "CropName": "Sắn",        "CropNameEN": "Cassava",
        "Category": "Cong nghiep","GrowthDurationDays": 270,
        "HarvestSeason": "Tháng 9-12",
        "TypicalPriceMin": 2000,  "TypicalPriceMax": 8000,
        "Description": "Sắn (mì) công nghiệp KM94, KM140 — nguyên liệu tinh bột",
    },
]


def seed_crops(verbose: bool = True) -> int:
    """Seed CropTypes. Trả về số cây trồng được thêm mới."""
    db = SessionLocal()
    added = 0
    updated = 0
    try:
        for data in CROPS_DATA:
            existing = db.query(CropType).filter(CropType.CropName == data["CropName"]).first()
            if existing:
                # Cập nhật các trường thiếu
                changed = False
                for field, value in data.items():
                    col = field  # CropName, GrowthDurationDays, ...
                    if getattr(existing, col, None) is None and value is not None:
                        setattr(existing, col, value)
                        changed = True
                if changed:
                    updated += 1
            else:
                db.add(CropType(**data))
                added += 1

        db.commit()
        if verbose:
            print(f"[Seed] CropTypes: +{added} mới, ~{updated} cập nhật "
                  f"(tổng {len(CROPS_DATA)} cây trong danh sách)")
    except Exception as e:
        db.rollback()
        print(f"[Seed] Lỗi: {e}")
        raise
    finally:
        db.close()
    return added


if __name__ == "__main__":
    seed_crops()
