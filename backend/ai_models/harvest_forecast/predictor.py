"""
P2-02: Harvest Predictor
Nhận crop_name, region, planting_date, weather_data
Trả về expected_harvest_date, confidence, warning, recommendation
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# Bảng thời gian sinh trưởng mặc định (ngày) theo loại cây
CROP_GROWTH_DAYS: Dict[str, int] = {
    # Rau
    "Cà chua":     75,
    "Cà tím":      70,
    "Dưa chuột":   60,
    "Bí đỏ":       90,
    "Bí xanh":     85,
    "Ớt":          90,
    "Đậu cove":    55,
    "Đậu bắp":     60,
    "Rau muống":   30,
    "Cải xanh":    45,
    "Cải ngọt":    40,
    "Rau cải":     45,
    "Xà lách":     35,
    "Rau ngót":    60,
    # Củ quả
    "Khoai lang":  110,
    "Khoai tây":   90,
    "Cà rốt":      80,
    "Củ cải":      60,
    "Hành tây":    120,
    "Tỏi":         150,
    # Trái cây / dài ngày
    "Dưa hấu":     80,
    "Dưa lê":      75,
    "Thanh long":  30,   # sau khi ra hoa
    "Xoài":        120,
    "Chuối":       270,
    "Mít":         150,
    "Bưởi":        240,
    "Cam":         210,
    "Sầu riêng":   90,   # sau khi ra hoa
    # Nông sản khác
    "Lúa":         105,
    "Ngô":         90,
    "Đậu nành":    100,
    "Lạc":         110,
}

# Ngưỡng cảnh báo thời tiết
WEATHER_WARNINGS = {
    "high_temp":     {"threshold": 38, "warning": "Nhiệt độ quá cao (>38°C) có thể làm chậm sinh trưởng."},
    "low_temp":      {"threshold": 10, "warning": "Nhiệt độ thấp (<10°C) có nguy cơ sương muối hại cây."},
    "high_rainfall": {"threshold": 200, "warning": "Mưa lớn có thể gây ngập úng, cần thoát nước kịp thời."},
    "low_humidity":  {"threshold": 30,  "warning": "Độ ẩm thấp – cần tăng cường tưới nước."},
    "high_humidity": {"threshold": 90,  "warning": "Độ ẩm cao có nguy cơ phát sinh nấm bệnh."},
}


class HarvestPredictor:
    """
    Dự báo thu hoạch dựa trên rule-based + điều chỉnh theo thời tiết.
    Có thể tích hợp Prophet model khi có dữ liệu huấn luyện.
    """

    def predict(
        self,
        crop_name: str,
        planting_date: datetime,
        region: str,
        growth_duration_days: Optional[int] = None,
        weather_data: Optional[Dict] = None,
    ) -> Dict:
        """
        Dự báo ngày thu hoạch.

        Args:
            crop_name:            Tên cây trồng
            planting_date:        Ngày trồng
            region:               Khu vực
            growth_duration_days: Thời gian sinh trưởng từ DB (ưu tiên hơn bảng mặc định)
            weather_data:         Dict với các key: temperature, rainfall, humidity

        Returns:
            {
                expected_harvest_date: str (ISO),
                confidence: float,
                growth_days: int,
                warning: str | None,
                recommendation: str,
            }
        """
        # 1. Xác định thời gian sinh trưởng
        base_days = (
            growth_duration_days
            or CROP_GROWTH_DAYS.get(crop_name)
            or 60  # mặc định 60 ngày nếu không có thông tin
        )

        # 2. Điều chỉnh theo thời tiết
        adjustment_days, warnings = self._weather_adjustment(weather_data or {})
        total_days = max(base_days + adjustment_days, base_days)

        # 3. Tính ngày thu hoạch
        expected_date = planting_date + timedelta(days=total_days)

        # 4. Tính confidence
        confidence = self._calc_confidence(
            crop_name=crop_name,
            has_weather=bool(weather_data),
            from_db=growth_duration_days is not None,
        )

        # 5. Khuyến nghị
        recommendation = self._get_recommendation(crop_name, region, expected_date, warnings)

        return {
            "expected_harvest_date": expected_date.date().isoformat(),
            "confidence":            round(confidence, 2),
            "growth_days":           total_days,
            "warning":               "; ".join(warnings) if warnings else None,
            "recommendation":        recommendation,
        }

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _weather_adjustment(self, weather: Dict) -> tuple:
        """Điều chỉnh số ngày và thu thập cảnh báo theo thời tiết."""
        adjustment = 0
        warnings: List[str] = []

        temp = weather.get("temperature") or weather.get("temp_max")
        rainfall = weather.get("rainfall")
        humidity = weather.get("humidity")

        if temp is not None:
            if temp > WEATHER_WARNINGS["high_temp"]["threshold"]:
                adjustment += 5
                warnings.append(WEATHER_WARNINGS["high_temp"]["warning"])
            elif temp < WEATHER_WARNINGS["low_temp"]["threshold"]:
                adjustment += 7
                warnings.append(WEATHER_WARNINGS["low_temp"]["warning"])

        if rainfall is not None and rainfall > WEATHER_WARNINGS["high_rainfall"]["threshold"]:
            adjustment += 3
            warnings.append(WEATHER_WARNINGS["high_rainfall"]["warning"])

        if humidity is not None:
            if humidity < WEATHER_WARNINGS["low_humidity"]["threshold"]:
                warnings.append(WEATHER_WARNINGS["low_humidity"]["warning"])
            elif humidity > WEATHER_WARNINGS["high_humidity"]["threshold"]:
                adjustment += 2
                warnings.append(WEATHER_WARNINGS["high_humidity"]["warning"])

        return adjustment, warnings

    @staticmethod
    def _calc_confidence(crop_name: str, has_weather: bool, from_db: bool) -> float:
        base = 0.70
        if crop_name in CROP_GROWTH_DAYS:
            base += 0.10
        if from_db:
            base += 0.08
        if has_weather:
            base += 0.05
        return min(base, 0.95)

    @staticmethod
    def _get_recommendation(
        crop_name: str, region: str, harvest_date: datetime, warnings: List[str]
    ) -> str:
        lines = [
            f"Dự kiến thu hoạch {crop_name} tại {region} vào {harvest_date.strftime('%d/%m/%Y')}.",
            "Chuẩn bị nhân lực và thiết bị trước 1 tuần.",
            "Theo dõi thời tiết thường xuyên để điều chỉnh kế hoạch.",
        ]
        if warnings:
            lines.append("Lưu ý: " + " | ".join(warnings))
        return " ".join(lines)


# Singleton instance
harvest_predictor = HarvestPredictor()
