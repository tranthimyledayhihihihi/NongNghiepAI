import re
import unicodedata


GREETING_REPLY = (
    "Chào bạn 👋 Mình là trợ lý AI nông nghiệp. Bạn muốn mình hỗ trợ về giá nông sản, "
    "thời tiết, mùa vụ, chất lượng hay cảnh báo rủi ro hôm nay?"
)

GENERAL_CAPABILITY_REPLY = (
    "Mình có thể hỗ trợ bạn theo 5 nhóm chính: phân tích giá nông sản, thời tiết canh tác, "
    "mùa vụ/thu hoạch, chất lượng nông sản và cảnh báo rủi ro. Bạn chỉ cần hỏi rõ nội dung, "
    "ví dụ: “giá cà chua ở Hà Nội hôm nay”, “hôm nay có nên tưới lúa không?” hoặc "
    "“mùa vụ của tôi khi nào thu hoạch?”."
)

ANALYSIS_INTENTS = {
    "price_analysis",
    "weather_analysis",
    "harvest_analysis",
    "quality_analysis",
    "alert_analysis",
    "full_farm_analysis",
}

INTENT_ALIASES = {
    "general": "general_question",
    "price": "price_analysis",
    "price_query": "price_analysis",
    "weather": "weather_analysis",
    "weather_advice": "weather_analysis",
    "harvest": "harvest_analysis",
    "harvest_advice": "harvest_analysis",
    "quality": "quality_analysis",
    "quality_check": "quality_analysis",
    "alert": "alert_analysis",
    "alert_summary": "alert_analysis",
    "dashboard": "full_farm_analysis",
    "farm": "full_farm_analysis",
    "agriculture": "full_farm_analysis",
}

DB_TOPIC_BY_INTENT = {
    "price_analysis": "Gia ca",
    "price_query": "Gia ca",
    "price": "Gia ca",
    "weather_analysis": "Thoi tiet",
    "weather_advice": "Thoi tiet",
    "weather": "Thoi tiet",
    "harvest_analysis": "Thu hoach",
    "harvest_advice": "Thu hoach",
    "harvest": "Thu hoach",
    "quality_analysis": "Chat luong",
    "quality_check": "Chat luong",
    "quality": "Chat luong",
    "pest": "Dich benh",
    "greeting": "Khac",
    "general_question": "Khac",
    "general": "Khac",
    "alert_analysis": "Khac",
    "alert_summary": "Khac",
    "full_farm_analysis": "Khac",
    "cultivation": "Khac",
    "soil_salinity": "Khac",
    "soil_acidity": "Khac",
    "agriculture": "Khac",
}

REGION_KEYWORDS: dict[str, str] = {
    "da nang": "Đà Nẵng",
    "ha noi": "Hà Nội",
    "ho chi minh": "TP.HCM",
    "tp hcm": "TP.HCM",
    "tphcm": "TP.HCM",
    "hcm": "TP.HCM",
    "sai gon": "TP.HCM",
    "can tho": "Cần Thơ",
    "gia lai": "Gia Lai",
    "dak lak": "Đắk Lắk",
    "dak nong": "Đắk Nông",
    "binh phuoc": "Bình Phước",
    "tien giang": "Tiền Giang",
    "dong nai": "Đồng Nai",
    "lam dong": "Lâm Đồng",
    "da lat": "Đà Lạt",
    "an giang": "An Giang",
    "bac giang": "Bắc Giang",
    "ben tre": "Bến Tre",
    "binh dinh": "Bình Định",
    "binh duong": "Bình Dương",
    "binh thuan": "Bình Thuận",
    "dong thap": "Đồng Tháp",
    "ha giang": "Hà Giang",
    "hai duong": "Hải Dương",
    "hau giang": "Hậu Giang",
    "hung yen": "Hưng Yên",
    "khanh hoa": "Khánh Hòa",
    "kien giang": "Kiên Giang",
    "kon tum": "Kon Tum",
    "long an": "Long An",
    "nghe an": "Nghệ An",
    "quang ngai": "Quảng Ngãi",
    "soc trang": "Sóc Trăng",
    "son la": "Sơn La",
    "tay ninh": "Tây Ninh",
    "vinh long": "Vĩnh Long",
}


def normalize_user_text(message: str) -> str:
    text = unicodedata.normalize("NFD", (message or "").lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_intent(intent: str | None) -> str:
    normalized = (intent or "general_question").strip()
    return INTENT_ALIASES.get(normalized, normalized)


def db_topic_for_intent(intent: str | None) -> str:
    return DB_TOPIC_BY_INTENT.get(intent or "", DB_TOPIC_BY_INTENT.get(normalize_intent(intent), "Khac"))


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _has_word(text: str, word: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", text) is not None


def _is_greeting_only(text: str) -> bool:
    if not text:
        return False
    greeting_phrases = {
        "chao",
        "chao ban",
        "xin chao",
        "hello",
        "hi",
        "alo",
        "ban oi",
        "chao ad",
        "chao anh",
        "chao chi",
        "chao em",
        "hey",
    }
    if text in greeting_phrases:
        return True
    words = text.split()
    if len(words) <= 4:
        return text.startswith(("chao ", "xin chao", "hello", "hi ", "alo", "hey ", "ban oi"))
    return False


def classify_user_intent(message: str) -> str:
    """Rule-based classifier for the AI Chat router.

    The rules intentionally avoid treating the normalized word "ban" as "bán"
    by itself because it is also the common greeting word "bạn".
    """
    text = normalize_user_text(message)
    if not text:
        return "general_question"

    full_farm_keywords = (
        "phan tich tong quan",
        "tong quan hom nay",
        "tinh hinh nong trai",
        "tinh hinh trang trai",
        "phan tich tinh hinh nong trai",
        "phan tich tinh hinh trang trai",
        "cho toi loi khuyen hom nay",
        "loi khuyen hom nay",
        "hom nay nen lam gi",
        "bao cao tong hop",
        "tong hop hom nay",
    )
    price_keywords = (
        "gia ca",
        "gia nong san",
        "thi truong",
        "du bao gia",
        "xu huong gia",
        "bao nhieu tien",
        "co nen ban",
        "nen ban",
        "ban khong",
        "ban hang",
        "giu hang",
        "giu lai",
        "xuat hang",
        "thu mua",
        "dinh gia",
    )
    weather_keywords = (
        "thoi tiet",
        "du bao thoi tiet",
        "mua khong",
        "co mua",
        "troi mua",
        "mua lon",
        "nang",
        "nang nong",
        "tuoi",
        "nen tuoi",
        "co nen tuoi",
        "phun",
        "do am",
        "nhiet do",
        "bao so",
        "giong bao",
        "ap thap",
        "lu lut",
        "lu quet",
        "han han",
        "ret",
        "suong muoi",
        "ngap",
        "rui ro thoi tiet",
    )
    harvest_keywords = (
        "mua vu",
        "thu hoach",
        "lich thu hoach",
        "khi nao thu hoach",
        "ngay cat",
        "xuong giong",
        "gieo sa",
        "gieo trong",
        "lich gieo",
        "ngay du kien thu hoach",
        "giai doan hien tai",
    )
    quality_keywords = (
        "chat luong",
        "loai may",
        "loai 1",
        "loai mot",
        "loai 2",
        "loai hai",
        "loai 3",
        "loai ba",
        "sau benh",
        "sau hai",
        "benh",
        "anh nay",
        "hinh anh",
        "hinh nay",
        "kiem dinh",
        "kiem tra chat luong",
        "nong san cua toi",
        "dau hieu benh",
        "la vang",
        "dom la",
    )
    alert_keywords = (
        "canh bao",
        "rui ro",
        "nguy hiem",
        "can chu y gi",
        "luu y gi",
        "co canh bao gi",
        "bat thuong",
    )
    general_keywords = (
        "ban lam duoc gi",
        "ai nay ho tro gi",
        "ho tro gi",
        "huong dan",
        "cach dung",
        "su dung he thong",
        "chuc nang",
        "tro ly nay",
        "gioi thieu",
    )

    if _contains_any(text, full_farm_keywords):
        return "full_farm_analysis"
    if _contains_any(text, price_keywords) or _has_word(text, "gia"):
        return "price_analysis"
    if _contains_any(text, weather_keywords) or _has_word(text, "gio"):
        return "weather_analysis"
    if _contains_any(text, harvest_keywords):
        return "harvest_analysis"
    if _contains_any(text, quality_keywords):
        return "quality_analysis"
    if _contains_any(text, alert_keywords):
        return "alert_analysis"
    if _is_greeting_only(text):
        return "greeting"
    if _contains_any(text, general_keywords):
        return "general_question"
    return "general_question"


def is_capability_question(message: str) -> bool:
    text = normalize_user_text(message)
    return _contains_any(
        text,
        (
            "ban lam duoc gi",
            "ai nay ho tro gi",
            "ho tro gi",
            "huong dan",
            "cach dung",
            "su dung he thong",
            "chuc nang",
            "tro ly nay",
            "gioi thieu",
        ),
    )


def extract_region_from_message(message: str) -> str | None:
    text = normalize_user_text(message)
    for keyword, region in REGION_KEYWORDS.items():
        if keyword in text:
            return region
    return None


def extract_crop_from_message(message: str) -> str | None:
    text = normalize_user_text(message)
    if not text:
        return None
    try:
        from app.services.pricing_service import pricing_service

        crops = pricing_service.crop_base_prices.keys()
    except Exception:
        crops = (
            "ca chua",
            "lua",
            "ngo",
            "sau rieng",
            "ca phe",
            "ho tieu",
            "tieu",
            "xoai",
            "thanh long",
            "chuoi",
        )
    for crop in sorted(crops, key=len, reverse=True):
        if normalize_user_text(crop) in text:
            return crop
    return None
