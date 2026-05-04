"""
P2-05: Quality Service
Lưu ảnh upload → gọi detector → phân loại Loại 1/2/3 → phát hiện sâu bệnh/hư hỏng.
POST /api/quality/check trả quality_grade và suggested_price.
"""
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Dict, Optional

from sqlalchemy.orm import Session

from ..models.crop import CropType, QualityRecord


UPLOAD_DIR = Path("uploads/quality_check")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class QualityService:
    """Service kiểm tra chất lượng nông sản qua ảnh AI."""

    @staticmethod
    def _get_detector():
        try:
            from ai_models.quality_check.detector import quality_detector
            return quality_detector
        except ImportError:
            # Fallback sang yolo_inference cũ nếu cần
            try:
                from ai_models.yolo_inference import quality_detector
                return quality_detector
            except ImportError:
                return None

    # ------------------------------------------------------------------ #
    # Phương thức chính
    # ------------------------------------------------------------------ #

    def check_quality(
        self,
        db: Session,
        image_path: str,
        crop_name: str,
        region: str,
        user_id: Optional[int] = None,
    ) -> Dict:
        """
        Kiểm tra chất lượng:
        1. Gọi detector phân tích ảnh
        2. Điều chỉnh giá theo giá thị trường nếu có DB
        3. Lưu kết quả vào QualityRecord
        4. Trả về kết quả đầy đủ
        """
        detector = self._get_detector()
        if detector:
            analysis = detector.detect_quality(image_path)
        else:
            analysis = self._mock_analysis()

        # Lấy CropID để lưu DB
        crop = (
            db.query(CropType)
            .filter(CropType.CropName == crop_name)
            .first()
        )

        # Lưu kết quả vào DB (nếu có crop)
        if crop and user_id:
            self._save_quality_record(
                db=db,
                crop_id=crop.CropID,
                user_id=user_id,
                image_path=image_path,
                analysis=analysis,
            )

        # Điều chỉnh giá từ DB nếu có
        price_range = self._adjust_price_from_db(
            db=db, crop=crop, grade=analysis["quality_grade"]
        )

        return {
            "crop_name":         crop_name,
            "region":            region,
            "quality_grade":     analysis["quality_grade"],
            "confidence":        analysis["confidence"],
            "disease_detected":  analysis.get("disease_detected", False),
            "damage_level":      analysis.get("damage_level", "none"),
            "defects":           analysis.get("defects", []),
            "suggested_price_min": price_range["min"],
            "suggested_price_max": price_range["max"],
            "recommendations":   analysis.get("recommendations", []),
        }

    def save_upload(self, file_content: bytes, filename: str) -> str:
        """Lưu file ảnh upload và trả về đường dẫn."""
        ext = Path(filename).suffix or ".jpg"
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}{ext}"
        with open(file_path, "wb") as f:
            f.write(file_content)
        return str(file_path)

    def cleanup_image(self, image_path: str):
        """Xóa file ảnh tạm sau khi xử lý."""
        try:
            if os.path.exists(image_path):
                os.unlink(image_path)
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _save_quality_record(
        db: Session,
        crop_id: int,
        user_id: int,
        image_path: str,
        analysis: Dict,
    ):
        """Lưu kết quả kiểm tra vào bảng QualityRecords."""
        try:
            record = QualityRecord(
                UserID=user_id,
                CropID=crop_id,
                ImagePath=image_path,
                AIGrade=analysis["quality_grade"],
                ConfidenceScore=analysis.get("confidence", 0.0),
                DetectedIssues=json.dumps(analysis.get("defects", []), ensure_ascii=False),
                SuggestedPriceMin=analysis.get("suggested_price_min"),
                SuggestedPriceMax=analysis.get("suggested_price_max"),
                Recommendation="\n".join(analysis.get("recommendations", [])),
            )
            db.add(record)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Warning: cannot save QualityRecord: {e}")

    @staticmethod
    def _adjust_price_from_db(db: Session, crop: Optional[CropType], grade: str) -> Dict:
        """
        Điều chỉnh khung giá dựa trên TypicalPrice từ CropTypes.
        Nếu không có dữ liệu DB thì dùng giá mặc định theo grade.
        """
        default_ranges = {
            "Loại 1": {"min": 25000, "max": 35000},
            "Loại 2": {"min": 15000, "max": 24000},
            "Loại 3": {"min": 8000,  "max": 14000},
            # backward-compat với grade_1/grade_2/grade_3 cũ
            "grade_1": {"min": 25000, "max": 35000},
            "grade_2": {"min": 15000, "max": 24000},
            "grade_3": {"min": 8000,  "max": 14000},
        }
        base = default_ranges.get(grade, {"min": 10000, "max": 20000})

        if crop and crop.TypicalPriceMin and crop.TypicalPriceMax:
            typical_min = float(crop.TypicalPriceMin)
            typical_max = float(crop.TypicalPriceMax)
            multipliers = {
                "Loại 1": (0.9, 1.1), "grade_1": (0.9, 1.1),
                "Loại 2": (0.6, 0.85), "grade_2": (0.6, 0.85),
                "Loại 3": (0.3, 0.55), "grade_3": (0.3, 0.55),
            }
            lo, hi = multipliers.get(grade, (0.5, 0.8))
            return {
                "min": int(typical_min * lo + typical_max * (1 - hi)),
                "max": int(typical_max * hi),
            }
        return base

    @staticmethod
    def _mock_analysis() -> Dict:
        """Mock khi không có detector."""
        return {
            "quality_grade":  "Loại 1",
            "confidence":     0.85,
            "disease_detected": False,
            "damage_level":   "none",
            "defects":        [],
            "suggested_price_min": 25000,
            "suggested_price_max": 35000,
            "recommendations": ["Chất lượng tốt – phù hợp bán trực tiếp."],
        }


quality_service = QualityService()
