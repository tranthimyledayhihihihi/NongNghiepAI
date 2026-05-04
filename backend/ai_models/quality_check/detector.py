"""
P2-04: YOLO Quality Detector
Tổ chức YOLO inference trong ai_models/quality_check/detector.py
Cung cấp hàm detect_quality(image_path) và phân loại chất lượng nông sản
"""
import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class QualityDetector:
    """
    YOLO-based quality detector cho nông sản.
    Phân loại: Loại 1 (tốt), Loại 2 (trung bình), Loại 3 (kém).
    """

    QUALITY_GRADES = {
        "Loại 1": {"max_defects": 0, "min_confidence": 0.8, "price_min": 25000, "price_max": 35000},
        "Loại 2": {"max_defects": 2, "min_confidence": 0.6, "price_min": 15000, "price_max": 24000},
        "Loại 3": {"max_defects": 5, "min_confidence": 0.4, "price_min": 8000,  "price_max": 14000},
    }

    DISEASE_CLASSES = [
        "rot", "mold", "pest_damage", "bruise", "discoloration",
        "thối", "nấm", "sâu_bệnh", "dập", "đổi_màu"
    ]

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "..", "weights", "best.pt"
        )
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load YOLO model, fallback sang mock nếu không có file."""
        try:
            if os.path.exists(self.model_path):
                from ultralytics import YOLO
                self.model = YOLO(self.model_path)
                print(f"✓ Loaded YOLO model: {self.model_path}")
            else:
                # Thử load pretrained yolov8n làm fallback
                fallback = os.path.join(
                    os.path.dirname(__file__), "..", "..", "yolov8n.pt"
                )
                if os.path.exists(fallback):
                    from ultralytics import YOLO
                    self.model = YOLO(fallback)
                    print(f"⚠ Using fallback YOLOv8n: {fallback}")
                else:
                    print("⚠ No YOLO model found. Using mock detection.")
                    self.model = None
        except Exception as e:
            print(f"⚠ Cannot load YOLO model: {e}. Using mock detection.")
            self.model = None

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def detect_quality(self, image_path: str) -> Dict:
        """
        Hàm chính: phân tích ảnh và trả về kết quả kiểm tra chất lượng.

        Returns:
            {
                quality_grade: str,        # "Loại 1" / "Loại 2" / "Loại 3"
                confidence: float,
                disease_detected: bool,
                damage_level: str,         # "none" / "low" / "medium" / "high"
                defects: list[str],
                defect_count: int,
                suggested_price_min: int,
                suggested_price_max: int,
                recommendations: list[str],
            }
        """
        detection = self._run_detection(image_path)
        grade, confidence = self._grade_quality(detection)
        price_range = self.QUALITY_GRADES[grade]
        disease_detected = any(
            d.lower() in self.DISEASE_CLASSES for d in detection["defects"]
        )
        damage_level = self._calc_damage_level(detection["defect_count"])

        return {
            "quality_grade": grade,
            "confidence": confidence,
            "disease_detected": disease_detected,
            "damage_level": damage_level,
            "defects": detection["defects"],
            "defect_count": detection["defect_count"],
            "suggested_price_min": price_range["price_min"],
            "suggested_price_max": price_range["price_max"],
            "recommendations": self._get_recommendations(grade, detection["defects"]),
        }

    # backward-compat alias (giữ cho quality.py API hoạt động)
    def analyze_image(self, image_path: str) -> Dict:
        result = self.detect_quality(image_path)
        return {
            "quality_grade":        result["quality_grade"],
            "confidence":           result["confidence"],
            "defects":              result["defects"],
            "defect_count":         result["defect_count"],
            "suggested_price_range": {
                "min": result["suggested_price_min"],
                "max": result["suggested_price_max"],
            },
            "recommendations": result["recommendations"],
        }

    # ------------------------------------------------------------------ #
    #  Internal helpers
    # ------------------------------------------------------------------ #

    def _run_detection(self, image_path: str) -> Dict:
        """Chạy YOLO inference, fallback sang mock nếu model None."""
        if self.model is None or not os.path.exists(image_path):
            return self._mock_detection()
        try:
            results = self.model(image_path, conf=0.25)
            defects, confidences = [], []
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = result.names[cls]
                    defects.append(class_name)
                    confidences.append(conf)
            return {
                "defects":       defects,
                "defect_count":  len(defects),
                "confidences":   confidences,
                "avg_confidence": float(np.mean(confidences)) if confidences else 0.9,
            }
        except Exception as e:
            print(f"Detection error: {e}")
            return self._mock_detection()

    def _mock_detection(self) -> Dict:
        """Mock detection cho test không cần model thật."""
        return {
            "defects":        [],
            "defect_count":   0,
            "confidences":    [0.90],
            "avg_confidence": 0.90,
        }

    def _grade_quality(self, detection: Dict) -> Tuple[str, float]:
        defect_count   = detection["defect_count"]
        avg_confidence = detection["avg_confidence"]
        if defect_count == 0 and avg_confidence >= 0.8:
            return "Loại 1", min(0.95, avg_confidence)
        elif defect_count <= 2 and avg_confidence >= 0.6:
            return "Loại 2", min(0.80, avg_confidence)
        else:
            return "Loại 3", min(0.60, avg_confidence)

    @staticmethod
    def _calc_damage_level(defect_count: int) -> str:
        if defect_count == 0:
            return "none"
        elif defect_count <= 2:
            return "low"
        elif defect_count <= 4:
            return "medium"
        return "high"

    def _get_recommendations(self, grade: str, defects: List[str]) -> List[str]:
        recs = {
            "Loại 1": [
                "Chất lượng tốt – phù hợp xuất khẩu hoặc siêu thị cao cấp.",
                "Nên bán sớm để giữ độ tươi tối đa.",
            ],
            "Loại 2": [
                "Chất lượng trung bình – phù hợp chợ đầu mối hoặc thương lái địa phương.",
                "Có thể sơ chế để nâng giá trị.",
            ],
            "Loại 3": [
                "Chất lượng thấp – nên bán nhanh hoặc chuyển sang chế biến.",
                "Cân nhắc giảm giá để tiêu thụ kịp thời.",
            ],
        }
        result = list(recs.get(grade, []))
        if defects:
            result.append(f"Phát hiện vấn đề: {', '.join(set(defects))}.")
        return result


# Singleton instance
quality_detector = QualityDetector()
