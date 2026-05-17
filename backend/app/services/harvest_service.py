from datetime import date, datetime, timedelta
from typing import Dict, Optional
from unicodedata import category, normalize

from sqlalchemy.orm import Session

from app.repositories.harvest_repository import (
    create_harvest_forecast,
    get_harvest_forecast_history,
    get_harvest_schedules_by_user,
)
from app.repositories.common import ensure_crop
from app.schemas.harvest_schema import HarvestForecastRequest, HarvestScheduleCreateRequest


class HarvestService:
    # Thời gian sinh trưởng (ngày) từ khi trồng cây giống đến thu hoạch đầu tiên.
    # Cây lâu năm (sầu riêng, xoài, cà phê...) tính theo năm trồng mới.
    # Cây ngắn ngày tính theo vụ.
    default_growth_days = {
        # ── Rau màu ngắn ngày ──────────────────────────────
        "ca chua":    75,   # Cà chua: 70-80 ngày
        "dua chuot":  60,   # Dưa chuột: 55-65 ngày
        "rau muong":  30,   # Rau muống: 25-35 ngày
        "cai xanh":   45,   # Cải xanh: 40-50 ngày
        "ot":         90,   # Ớt: 85-100 ngày
        "dua hau":    80,   # Dưa hấu: 70-90 ngày
        "khoai lang": 100,  # Khoai lang: 90-110 ngày
        "khoai tay":  90,   # Khoai tây: 80-100 ngày
        "hanh":       60,   # Hành tây: 55-70 ngày
        "toi":        90,   # Tỏi: 80-100 ngày
        "bap cai":    70,   # Bắp cải: 60-80 ngày
        "xup lo":     70,   # Súp lơ/Bông cải: 60-80 ngày
        # ── Ngũ cốc ────────────────────────────────────────
        "lua":       105,   # Lúa: 90-120 ngày (tùy giống)
        "ngo":        90,   # Ngô: 80-100 ngày
        "dau tuong":  95,   # Đậu tương: 85-110 ngày
        "dau phong": 120,   # Đậu phộng/Lạc: 110-130 ngày
        # ── Cây ăn quả lâu năm ────────────────────────────
        # (tính từ khi trồng cây giống ghép đến thu hoạch vụ đầu tiên)
        "sau rieng": 1460,  # Sầu riêng: 4-6 năm (cây giống ghép); từ ra hoa đến quả: 90-120 ngày
        "xoai":      1095,  # Xoài: 3-4 năm từ cây giống ghép
        "mit":       1460,  # Mít: 4-5 năm từ cây giống
        "bo":        1825,  # Bơ: 5-7 năm từ cây giống (giống ghép ~3 năm)
        "vai":        730,  # Vải: 2-3 năm từ cây giống ghép
        "nhan":       730,  # Nhãn: 2-3 năm từ cây giống ghép
        "chom chom":  730,  # Chôm chôm: 2-3 năm từ cây giống ghép
        "buoi":      1095,  # Bưởi: 3-4 năm từ cây giống ghép
        "cam":        730,  # Cam: 2-3 năm từ cây giống ghép
        "quyt":       730,  # Quýt: 2-3 năm từ cây giống ghép
        "chanh":      548,  # Chanh: 1.5-2 năm từ cây giống ghép
        "chuoi":      365,  # Chuối: 10-12 tháng từ khi trồng chồi
        "du du":      270,  # Đu đủ: 8-10 tháng từ hạt
        "dua":        365,  # Dứa/Khóm: 12-18 tháng từ chồi
        "thanh long":  540, # Thanh long: 18 tháng từ hom giống đến thu hoạch đầu tiên
        "mang cut":  1825,  # Măng cụt: 5-6 năm từ hạt (cây thực sinh)
        "sapoche":   1460,  # Sapôchê/Hồng xiêm: 4-5 năm từ cây giống
        "na":         548,  # Na/Mãng cầu: 1.5-2 năm từ cây giống
        # ── Cây công nghiệp ────────────────────────────────
        "ca phe":    1095,  # Cà phê: 3-4 năm từ cây giống
        "ho tieu":   1095,  # Hồ tiêu: 3-4 năm từ hom giống
        "cao su":    2555,  # Cao su: 7 năm từ khi trồng đến khai thác
        "dieu":      1460,  # Điều: 4-5 năm từ cây giống
        "mia":        365,  # Mía: 10-12 tháng từ hom giống
        "san":        270,  # Sắn/Mì: 8-12 tháng tùy giống
        "che":       1095,  # Chè (trà): 3-4 năm từ cây giống đến thu búp đầu tiên
    }

    # Mô tả giai đoạn sinh trưởng cho các loại cây phổ biến
    _growth_stages = {
        "sau rieng": [
            "Tháng 1-6: Cây giống, làm đất, trồng mới",
            "Năm 1-2: Nuôi cây, bón phân, cắt tỉa tạo tán",
            "Năm 2-3: Cây bắt đầu phân cành cấp 1, cấp 2",
            "Năm 3-4: Cây trưởng thành, có thể ra hoa vụ đầu",
            "Từ ra hoa → quả chín: 90-120 ngày (3-4 tháng)",
            "Thu hoạch: khi quả có mùi thơm, gai mềm, đường rãnh nở",
        ],
        "ca phe": [
            "Tháng 1-6: Ươm hạt, cây giống trong vườn ươm",
            "Năm 1-2: Trồng mới, bón phân, làm giàn che",
            "Năm 2-3: Cây phát triển bộ khung, tỉa cành",
            "Năm 3-4: Ra hoa lần đầu (hoa trắng thơm), đậu quả",
            "Thu hoạch: khi quả chín đỏ/vàng (9-11 tháng sau ra hoa)",
        ],
        "lua": [
            "Ngày 1-7: Ngâm ủ, gieo mạ hoặc sạ thẳng",
            "Ngày 7-25: Giai đoạn mạ / cây con",
            "Ngày 25-60: Đẻ nhánh, làm đòng",
            "Ngày 60-80: Trổ bông, phơi màu",
            "Ngày 80-105: Chín sữa → chín hoàn toàn",
        ],
        "thanh long": [
            "Tháng 1-3: Trồng hom, bám giàn",
            "Tháng 3-12: Nuôi cành, phát triển thân leo",
            "Tháng 12-18: Ra hoa lần đầu",
            "Từ ra hoa → thu hoạch: 28-35 ngày",
            "Cho trái quanh năm sau khi trưởng thành",
        ],
    }

    @staticmethod
    def _get_predictor():
        try:
            from ai_models.harvest_forecast.predictor import harvest_predictor

            return harvest_predictor
        except ImportError:
            return None

    def forecast_harvest(
        self,
        db: Session,
        request: HarvestForecastRequest,
        user_id: int | None = None,
    ) -> dict:
        crop_name = request.crop_name
        region = request.region
        planting_date = request.planting_date

        weather_data = self._get_latest_weather(db, region)
        growth_duration = self._resolve_growth_days(db, crop_name)

        predictor = self._get_predictor()
        if predictor:
            try:
                ai_result = predictor.predict(
                    crop_name=crop_name,
                    planting_date=datetime.combine(planting_date, datetime.min.time()),
                    region=region,
                    growth_duration_days=growth_duration,
                    weather_data=weather_data,
                )
                growth_days = ai_result.get("growth_days", self._growth_days_for(crop_name))
                expected_date = planting_date + timedelta(days=growth_days)
                warning = ai_result.get("warning") or self._warning_for(expected_date)
                recommendation = ai_result.get(
                    "recommendation",
                    f"Dự kiến thu hoạch sau {growth_days} ngày. Nên theo dõi thời tiết trước thu hoạch.",
                )
                confidence = ai_result.get("confidence", 0.78)
            except Exception:
                predictor = None

        if not predictor:
            growth_days = self._growth_days_for(crop_name)
            expected_date = planting_date + timedelta(days=growth_days)
            warning = self._warning_for(expected_date)
            years = growth_days // 365
            months = (growth_days % 365) // 30
            if years > 0:
                duration_str = f"{years} năm {months} tháng" if months else f"{years} năm"
            else:
                duration_str = f"{growth_days} ngày"
            recommendation = (
                f"Dự kiến thu hoạch {crop_name} tại {region} vào {expected_date.strftime('%d/%m/%Y')} "
                f"(sau {duration_str} kể từ ngày trồng). "
                "Chuẩn bị nhân lực và thiết bị trước 1-2 tuần. "
                "Theo dõi thời tiết thường xuyên để điều chỉnh kế hoạch."
            )
            confidence = 0.78

        growth_stages = self._get_growth_stages(crop_name)
        record = create_harvest_forecast(
            db,
            crop_name=crop_name,
            region=region,
            planting_date=planting_date,
            expected_harvest_date=expected_date,
            confidence=confidence,
            warning=warning,
            recommendation=recommendation,
            user_id=user_id,
        )

        return {
            "crop_name": crop_name,
            "region": region,
            "planting_date": planting_date,
            "expected_harvest_date": expected_date,
            "growth_days": growth_days if not predictor else self._growth_days_for(crop_name),
            "confidence": confidence,
            "warning": warning,
            "recommendation": recommendation,
            "growth_stages": growth_stages,
            "created_at": getattr(record, "created_at", None),
        }

    def predict_harvest_date(
        self,
        db: Session,
        crop_name: str,
        planting_date: datetime,
        region: str,
        user_id: int | None = None,
    ) -> dict:
        planting_day = planting_date.date() if hasattr(planting_date, "date") else planting_date
        request = HarvestForecastRequest(
            crop_name=crop_name,
            region=region,
            planting_date=planting_day,
        )
        result = self.forecast_harvest(db, request, user_id=user_id)
        return {
            **result,
            "predicted_harvest_date": result["expected_harvest_date"],
            "growth_days": self._growth_days_for(crop_name),
            "recommendations": [result["recommendation"]],
        }

    def create_harvest_schedule(
        self,
        db: Session,
        user_id: int,
        crop_id: int,
        region: str,
        planting_date: date,
        expected_harvest_date: date,
        area_size: Optional[float] = None,
        estimated_yield_kg: Optional[float] = None,
        notes: Optional[str] = None,
    ):
        try:
            from app.models.harvest import HarvestSchedule

            schedule = HarvestSchedule(
                UserID=user_id,
                CropID=crop_id,
                Region=region,
                PlantingDate=planting_date,
                ExpectedHarvestDate=expected_harvest_date,
                AreaSize=area_size,
                EstimatedYieldKg=estimated_yield_kg,
                Notes=notes,
            )
            db.add(schedule)
            db.commit()
            db.refresh(schedule)
            return schedule
        except Exception:
            db.rollback()
            return None

    def create_schedule_from_request(
        self,
        db: Session,
        user_id: int,
        request: HarvestScheduleCreateRequest,
    ) -> dict | None:
        try:
            from app.models.harvest import HarvestSchedule

            crop = ensure_crop(db, request.crop_name)
            expected_date = request.expected_harvest_date
            if expected_date is None:
                expected_date = request.planting_date + timedelta(days=self._resolve_growth_days(db, request.crop_name))

            schedule = HarvestSchedule(
                UserID=user_id,
                CropID=crop.CropID,
                Region=request.region,
                PlantingDate=request.planting_date,
                ExpectedHarvestDate=expected_date,
                AreaSize=request.area_size,
                EstimatedYieldKg=request.estimated_yield_kg,
                FertilizerUsed=request.fertilizer_used,
                PesticideUsed=request.pesticide_used,
                Notes=request.notes,
            )
            db.add(schedule)
            db.commit()
            db.refresh(schedule)
            return self._schedule_to_dict(schedule, crop)
        except Exception:
            db.rollback()
            return None

    def get_history(self, db: Session, user_id: int, limit: int = 50) -> list[dict]:
        records = get_harvest_forecast_history(db, user_id, limit)
        return [
            {
                "forecast_id": forecast.id,
                "schedule_id": schedule.id,
                "user_id": schedule.user_id,
                "crop_id": crop.id,
                "crop_name": crop.name,
                "region": schedule.region,
                "planting_date": schedule.planting_date,
                "expected_harvest_date": forecast.expected_harvest_date,
                "confidence": forecast.confidence_score,
                "warning": forecast.weather_warning,
                "recommendation": forecast.labor_recommendation,
                "transport_recommendation": forecast.transport_recommendation,
                "model_version": forecast.model_version,
                "generated_at": forecast.generated_at,
            }
            for forecast, schedule, crop in records
        ]

    def get_schedules(self, db: Session, user_id: int, limit: int = 50) -> list[dict]:
        records = get_harvest_schedules_by_user(db, user_id, limit)
        return [
            self._schedule_to_dict(schedule, crop)
            for schedule, crop in records
        ]

    @staticmethod
    def _schedule_to_dict(schedule, crop) -> dict:
        return {
            "schedule_id": schedule.id,
            "user_id": schedule.user_id,
            "crop_id": crop.id,
            "crop_name": crop.name,
            "crop_image": getattr(crop, "image_url", None),
            "planting_date": schedule.planting_date,
            "area_size": schedule.area_size,
            "unit": "hectare",
            "region": schedule.region,
            "expected_harvest_date": schedule.expected_harvest_date,
            "actual_harvest_date": schedule.actual_harvest_date,
            "estimated_yield_kg": schedule.estimated_yield_kg,
            "actual_yield_kg": schedule.actual_yield_kg,
            "fertilizer_used": getattr(schedule, "FertilizerUsed", None),
            "pesticide_used": getattr(schedule, "PesticideUsed", None),
            "status": schedule.status,
            "notes": schedule.notes,
            "created_at": schedule.created_at,
            "updated_at": schedule.updated_at,
        }

    def _growth_days_for(self, crop_name: str) -> int:
        key = self._normalize_key(crop_name)
        return self.default_growth_days.get(key, 120)  # default 120 ngày thay vì 70

    def _get_growth_stages(self, crop_name: str) -> list[str]:
        key = self._normalize_key(crop_name)
        return self._growth_stages.get(key, [])

    def _resolve_growth_days(self, db: Session, crop_name: str) -> int:
        key = self._normalize_key(crop_name)
        if key in self.default_growth_days:
            return self.default_growth_days[key]
        return self._get_crop_growth_days(db, crop_name) or self._growth_days_for(crop_name)

    def _get_crop_growth_days(self, db: Session, crop_name: str) -> Optional[int]:
        try:
            from app.models.crop import CropType

            crop = db.query(CropType).filter(CropType.CropName == crop_name).first()
            return crop.GrowthDurationDays if crop and crop.GrowthDurationDays else None
        except Exception:
            return None

    @staticmethod
    def _get_latest_weather(db: Session, region: str) -> Optional[Dict]:
        try:
            from app.models.weather import WeatherData

            weather = (
                db.query(WeatherData)
                .filter(WeatherData.Region == region)
                .order_by(WeatherData.RecordDate.desc())
                .first()
            )
            if not weather:
                return None
            return {
                "temperature": float(weather.TempMax) if weather.TempMax else None,
                "rainfall": float(weather.Rainfall) if weather.Rainfall else None,
                "humidity": float(weather.Humidity) if weather.Humidity else None,
            }
        except Exception:
            return None

    @staticmethod
    def _normalize_key(value: str) -> str:
        normalized = normalize("NFD", value.strip().lower())
        return "".join(char for char in normalized if category(char) != "Mn")

    @staticmethod
    def _warning_for(expected_date: date) -> str | None:
        if expected_date.month in {9, 10, 11}:
            return "Mùa mưa bão, cần theo dõi thời tiết và chuẩn bị thu hoạch sớm nếu cần."
        return None


harvest_service = HarvestService()
