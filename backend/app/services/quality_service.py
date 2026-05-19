"""
Quality Service - merged Tien (repository + pricing) + Quang (AI detector + DB records)
- API endpoint dùng: check_quality(db, *, image_path, crop_name, region)
- Thử AI detector trước, fallback về mock_grade
"""
import json
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.common import to_api_grade
from app.repositories.quality_repository import (
    create_quality_check,
    get_quality_check_by_id,
    get_quality_checks_by_user,
)
from app.schemas.price_schema import PricingSuggestRequest
from app.services.pricing_service import pricing_service


class QualityService:
    """Service kiểm tra chất lượng nông sản qua ảnh."""

    # ------------------------------------------------------------------ #
    # API interface
    # ------------------------------------------------------------------ #

    def check_quality(
        self,
        db: Session,
        *,
        image_path: str,
        crop_name: str,
        region: str,
        user_id: Optional[int] = None,
    ) -> dict:
        """
        Kiểm tra chất lượng nông sản:
        1. Gemini Vision phân tích ảnh thực tế (màu sắc, khuyết tật, loại nông sản)
        2. Lấy pricing từ pricing_service
        3. Lưu kết quả qua repository
        4. Trả về kết quả đầy đủ
        """
        # 1. Đọc ảnh và gọi Gemini Vision
        analyzer = self._get_detector()
        if analyzer is None:
            if self._realtime_only():
                return {
                    "_api_error": True,
                    "error_code": "REALTIME_API_FAILED",
                    "error_message": "Không thể kết nối AI kiểm định chất lượng. Vui lòng thử lại sau.",
                    "source": "realtime_api",
                }
            grade, confidence, defects = self._mock_grade(image_path)
            vision_result = {
                "detected_crop": crop_name or "unknown",
                "is_produce": True,
                "color_assessment": "",
                "ripeness": "unknown",
                "defects": defects,
                "quality_grade": grade,
                "confidence": confidence,
                "reasoning": "mock fallback",
            }
        else:
            try:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                if hasattr(analyzer, "analyze"):
                    vision_result = analyzer.analyze(image_bytes)
                else:
                    detector_result = analyzer.analyze_image(image_path, crop_name)
                    vision_result = self._vision_from_detector_result(detector_result, crop_name)
            except Exception as e:
                if self._realtime_only():
                    return {
                        "_api_error": True,
                        "error_code": "REALTIME_API_FAILED",
                        "error_message": "Không thể kết nối AI kiểm định chất lượng. Vui lòng thử lại sau.",
                        "source": "realtime_api",
                    }
                vision_result = {
                    "detected_crop": "không xác định",
                    "is_produce": False,
                    "color_assessment": f"Lỗi đọc ảnh: {e}",
                    "ripeness": "unknown",
                    "defects": [],
                    "quality_grade": "grade_2",
                    "confidence": 0.0,
                    "reasoning": str(e),
                }

        detected_crop = vision_result.get("detected_crop", "không xác định")
        is_produce = vision_result.get("is_produce", False)
        grade = vision_result.get("quality_grade", "grade_2")
        confidence = vision_result.get("confidence", 0.0)
        defects = vision_result.get("defects", [])
        color_assessment = vision_result.get("color_assessment", "")
        reasoning = vision_result.get("reasoning", "")
        if self._realtime_only() and float(confidence or 0) <= 0:
            return {
                "_api_error": True,
                "error_code": "REALTIME_API_FAILED",
                "error_message": "Không thể kết nối AI kiểm định chất lượng. Vui lòng thử lại sau.",
                "source": "realtime_api",
            }
        disease_detected = bool(defects)
        damage_level = self._damage_level(grade)

        # Nếu người dùng không nhập crop_name, dùng kết quả nhận diện
        effective_crop = crop_name if crop_name and crop_name not in ("unknown", "") else detected_crop

        # 2. Lấy giá thực từ DB/Tavily theo grade
        price_info = self._fetch_real_price(db, effective_crop, region, grade)
        if price_info.get("_api_error"):
            return price_info

        final_min       = price_info["min"]
        final_max       = price_info["max"]
        final_suggested = price_info["suggested"]

        # Cũng gọi pricing_service để lấy weather_factor (bổ sung thông tin)
        pricing = {}
        try:
            pricing = pricing_service.suggest_price(
                db,
                PricingSuggestRequest(
                    crop_name=effective_crop,
                    region=region,
                    quantity=1,
                    quality_grade=grade,
                ),
            )
        except Exception:
            pass

        # 3. Lưu vào DB qua repository
        record = create_quality_check(
            db,
            crop_name=effective_crop,
            region=region,
            image_path=image_path,
            quality_grade=grade,
            disease_detected=disease_detected,
            damage_level=damage_level,
            suggested_price=final_suggested,
            confidence=confidence,
        )

        # 4. Bổ sung lưu vào QualityRecord (Quang) nếu có crop + user
        self._save_quality_record_direct(
            db=db,
            crop_name=effective_crop,
            user_id=user_id,
            image_path=image_path,
            grade=grade,
            confidence=confidence,
            defects=defects,
            min_price=final_min,
            max_price=final_max,
            recommendations=self._recommendations(grade),
        )

        return {
            "crop_name": effective_crop,
            "detected_crop": detected_crop,
            "is_produce": is_produce,
            "color_assessment": color_assessment,
            "reasoning": reasoning,
            "region": region,
            "image_path": image_path,
            "quality_grade": grade,
            "quality_grade_letter": self._grade_letter(grade),
            "disease_detected": disease_detected,
            "disease_risk": damage_level,
            "damage_level": damage_level,
            "freshness_score": self._freshness_score(grade, defects),
            "suggested_price": final_suggested,
            "suggested_price_adjustment": f"{int((price_info.get('multiplier', 1.0) - 1) * 100)}%",
            "confidence": confidence,
            "defects": defects,
            "suggested_price_range": {
                "min": final_min,
                "max": final_max,
            },
            # Nguồn giá và hệ số chất lượng
            "price_source":        price_info.get("source", ""),
            "quality_multiplier":  price_info.get("multiplier", 1.0),
            # Thông tin thời tiết kèm theo
            "weather_factor":      pricing.get("weather_factor", 1.0),
            "weather_summary":     pricing.get("weather_summary", ""),
            "weather_explanation": pricing.get("weather_explanation", ""),
            "price_change_pct":    pricing.get("price_change_pct", 0.0),
            "recommendation": self._recommendations(grade),
            "recommendations": self._recommendations(grade),
            "source": "mock" if confidence == 0.0 or reasoning == "mock fallback" else "ai_generated",
            "source_name": "Gemini Vision Quality" if confidence > 0 else "Rule-based quality fallback",
            "is_mock": confidence == 0.0 or reasoning == "mock fallback",
            "cache_status": "computed",
            "checked_at": getattr(record, "checked_at", None) or datetime.now(),
        }

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _realtime_only() -> bool:
        return bool(settings.USE_REALTIME_ONLY) and not bool(settings.ALLOW_MOCK_DATA or settings.ALLOW_SAMPLE_DATA)

    @staticmethod
    def _get_detector():
        from app.integrations.gemini_vision_quality import GeminiVisionAnalyzer
        return GeminiVisionAnalyzer()

    @staticmethod
    def _vision_from_detector_result(result: dict, crop_name: str) -> dict:
        grade = result.get("quality_grade", "grade_2")
        defects = result.get("defects", [])
        return {
            "detected_crop": crop_name or "unknown",
            "is_produce": True,
            "color_assessment": "",
            "ripeness": "unknown",
            "defects": defects,
            "quality_grade": grade,
            "confidence": result.get("confidence", 0.0),
            "reasoning": ", ".join(defects) if defects else "",
        }

    @staticmethod
    def _save_quality_record_direct(
        db: Session,
        crop_name: str,
        user_id: Optional[int],
        image_path: str,
        grade: str,
        confidence: float,
        defects: list,
        min_price: float,
        max_price: float,
        recommendations: list,
    ):
        """Lưu vào bảng QualityRecords trực tiếp (Quang) - best-effort."""
        if not user_id:
            return
        _GRADE_MAP = {"grade_1": "Loai 1", "grade_2": "Loai 2", "grade_3": "Loai 3"}
        db_grade = _GRADE_MAP.get(grade, "Loai 2")
        try:
            from app.models.quality import QualityRecord
            from app.models.crop import CropType
            crop = db.query(CropType).filter(CropType.CropName.ilike(f"%{crop_name}%")).first()
            if not crop:
                return
            record = QualityRecord(
                UserID=user_id,
                CropID=crop.CropID,
                ImagePath=image_path,
                AIGrade=db_grade,
                ConfidenceScore=confidence,
                DetectedIssues=json.dumps(defects, ensure_ascii=False),
                SuggestedPriceMin=min_price,
                SuggestedPriceMax=max_price,
                Recommendation="\n".join(recommendations),
            )
            db.add(record)
            db.commit()
        except Exception as exc:
            db.rollback()
            print(f"Warning: cannot save QualityRecord: {exc}")

    def get_history(self, db: Session, user_id: int, limit: int = 50) -> list[dict]:
        return [
            self._record_to_dict(record, crop)
            for record, crop in get_quality_checks_by_user(db, user_id, limit)
        ]

    def get_detail(self, db: Session, record_id: int) -> dict | None:
        result = get_quality_check_by_id(db, record_id)
        if result is None:
            return None
        record, crop = result
        return self._record_to_dict(record, crop)

    # Hệ số giảm giá theo chất lượng
    _GRADE_MULTIPLIER = {"grade_1": 1.0, "grade_2": 0.78, "grade_3": 0.45}

    def _fetch_real_price(self, db: Session, crop_name: str, region: str, grade: str) -> dict:
        """
        Lấy giá thực từ MarketPrices DB cho crop_name.
        Áp hệ số chất lượng: grade_1=100%, grade_2=78%, grade_3=45%.
        Fallback về TypicalPrice nếu không có market data.
        """
        from app.models.crop import Crop
        from app.models.price import MarketPrice

        multiplier = self._GRADE_MULTIPLIER.get(grade, 0.78)

        # Tìm crop trong DB (fuzzy match, không phân biệt hoa thường)
        crop = (
            db.query(Crop)
            .filter(Crop.CropName.ilike(f"%{crop_name}%"))
            .first()
        )

        base_price: float | None = None

        if crop:
            # Ưu tiên lấy giá theo vùng, fallback toàn quốc
            mp = (
                db.query(MarketPrice)
                .filter(MarketPrice.CropID == crop.CropID, MarketPrice.Region == region)
                .order_by(MarketPrice.PriceDate.desc())
                .first()
            )
            if not mp:
                mp = (
                    db.query(MarketPrice)
                    .filter(MarketPrice.CropID == crop.CropID)
                    .order_by(MarketPrice.PriceDate.desc())
                    .first()
                )
            if mp:
                base_price = float(mp.PricePerKg)

            # Fallback về typical price nếu không có market price
            if base_price is None and crop.TypicalPriceMin and crop.TypicalPriceMax:
                base_price = (float(crop.TypicalPriceMin) + float(crop.TypicalPriceMax)) / 2

        # Nếu vẫn không tìm được, thử Tavily
        if base_price is None:
            try:
                import asyncio
                from app.core.config import settings
                from app.integrations.tavily_client import ask_price_qa
                result = asyncio.run(asyncio.wait_for(asyncio.to_thread(
                    ask_price_qa,
                    f"giá {crop_name} hiện nay tại {region} VNĐ/kg"
                ), timeout=settings.AI_TIMEOUT_SECONDS))
                import re
                nums = re.findall(r'\d[\d\.]{2,8}', result.get("tavily_answer", ""))
                if nums:
                    base_price = float(nums[0].replace(".", ""))
            except Exception:
                if self._realtime_only():
                    return {
                        "_api_error": True,
                        "error_code": "REALTIME_API_FAILED",
                        "error_message": "Không thể tải giá realtime cho kiểm định chất lượng.",
                        "source": "realtime_api",
                    }
                base_price = 20_000  # fallback tuyệt đối

        if base_price is None and self._realtime_only():
            return {
                "_api_error": True,
                "error_code": "REALTIME_API_FAILED",
                "error_message": "Không thể tải giá realtime cho kiểm định chất lượng.",
                "source": "realtime_api",
            }

        base_price = base_price or 20_000

        suggested = round(base_price * multiplier)
        spread = 0.08  # ±8%
        return {
            "suggested": suggested,
            "min":       round(suggested * (1 - spread)),
            "max":       round(suggested * (1 + spread)),
            "base_price": base_price,
            "multiplier": multiplier,
            "source": "market_db" if crop else "tavily",
        }

    @staticmethod
    def _mock_grade(image_path: str) -> tuple[str, float, list[str]]:
        """Phân loại dựa trên tên file (fallback khi không có AI)."""
        lowered = image_path.lower()
        if "bad" in lowered or "grade3" in lowered or "grade_3" in lowered:
            return "grade_3", 0.68, ["surface_damage"]
        if "medium" in lowered or "grade2" in lowered or "grade_2" in lowered:
            return "grade_2", 0.76, ["minor_spot"]
        return "grade_1", 0.86, []

    @staticmethod
    def _damage_level(grade: str) -> str:
        return {"grade_1": "low", "Loại 1": "low",
                "grade_2": "medium", "Loại 2": "medium",
                "grade_3": "high", "Loại 3": "high"}.get(grade, "low")

    @staticmethod
    def _grade_letter(grade: str) -> str:
        return {
            "grade_1": "A",
            "Loai 1": "A",
            "Loại 1": "A",
            "grade_2": "B",
            "Loai 2": "B",
            "Loại 2": "B",
            "grade_3": "C",
            "Loai 3": "C",
            "Loại 3": "C",
        }.get(grade, "B")

    @staticmethod
    def _freshness_score(grade: str, defects: list) -> int:
        base = {"grade_1": 92, "grade_2": 72, "grade_3": 48}.get(grade, 70)
        return max(20, min(100, base - len(defects or []) * 6))

    @staticmethod
    def _recommendations(grade: str) -> list[str]:
        if grade in ("grade_1", "Loai 1", "Loại 1"):
            return [
                "Ưu tiên bán kênh siêu thị, cửa hàng sạch hoặc xuất khẩu.",
                "Đóng gói đẹp để tăng giá trị thương phẩm.",
            ]
        if grade in ("grade_2", "Loai 2", "Loại 2"):
            return [
                "Phù hợp cho chợ đầu mối hoặc thương lái địa phương.",
                "Giá bán thấp hơn ~22% so với loại 1.",
            ]
        return [
            "Nên bán nhanh hoặc chuyển sang kênh chế biến để giảm hao hụt.",
            "Giá bán chỉ đạt ~45% giá thị trường — cân nhắc làm nước ép, sấy khô.",
        ]

    @staticmethod
    def _record_to_dict(record, crop) -> dict:
        issues = QualityService._parse_issues(record.detected_issues)
        suggested_min = float(record.suggested_price_min or 0)
        suggested_max = float(record.suggested_price_max or 0)
        suggested_price = round((suggested_min + suggested_max) / 2, 2) if suggested_min or suggested_max else 0
        grade = to_api_grade(record.quality_grade)
        return {
            "record_id": record.RecordID,
            "schedule_id": record.ScheduleID,
            "user_id": record.UserID,
            "crop_id": crop.CropID,
            "crop_name": crop.CropName,
            "image_path": record.image_path,
            "quality_grade": grade,
            "disease_detected": bool(issues.get("disease_detected", False)),
            "damage_level": issues.get("damage_level") or QualityService._damage_level(grade),
            "suggested_price": suggested_price,
            "confidence": float(record.ConfidenceScore or 0),
            "defects": issues.get("defects", []),
            "suggested_price_range": {
                "min": suggested_min,
                "max": suggested_max,
            },
            "recommendation": record.Recommendation,
            "recommendations": QualityService._recommendations(grade),
            "checked_at": record.CheckDate,
        }

    @staticmethod
    def _parse_issues(raw: str | None) -> dict:
        if not raw:
            return {}
        try:
            issues = json.loads(raw)
        except (TypeError, ValueError):
            return {"defects": [raw]}
        if not isinstance(issues, dict):
            return {"defects": issues if isinstance(issues, list) else [str(issues)]}
        defects = issues.get("defects")
        if defects is None and issues.get("disease_detected"):
            defects = ["detected_issue"]
        return {**issues, "defects": defects or []}


quality_service = QualityService()
