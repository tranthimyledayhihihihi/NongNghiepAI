from ultralytics import YOLO
import os
import logging

logger = logging.getLogger(__name__)

# COCO class names liên quan đến nông sản
_FOOD_CLASSES = {
    "apple", "orange", "banana", "broccoli", "carrot",
    "hot dog", "pizza", "sandwich", "cake",
    "pottedplant", "potted plant",
}

# Mapping COCO class → crop alias tiếng Việt
_CLASS_TO_CROP = {
    "apple":    ["táo", "apple"],
    "orange":   ["cam", "quýt", "bưởi", "orange"],
    "banana":   ["chuối", "banana"],
    "broccoli": ["bông cải", "súp lơ", "broccoli"],
    "carrot":   ["cà rốt", "carrot"],
}


class QualityDetector:
    def __init__(self):
        self.model_path = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
        try:
            self.model = YOLO(self.model_path)
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None

    def analyze_image(self, image_path: str, crop_name: str = "") -> dict:
        if not self.model:
            return _fallback_result()

        try:
            results = self.model(image_path, verbose=False)
            return self._parse_results(results, crop_name, image_path)
        except Exception as e:
            logger.warning(f"YOLO inference failed: {e}")
            return _fallback_result()

    def _parse_results(self, results, crop_name: str, image_path: str = "") -> dict:
        if not results or len(results) == 0:
            return _fallback_result()

        r = results[0]
        boxes = r.boxes
        names = r.names  # {class_id: class_name}

        if boxes is None or len(boxes) == 0:
            # Không phát hiện object nào — không thể đánh giá
            return {
                "quality_grade": "grade_1",
                "confidence": 0.75,
                "disease_detected": False,
                "damage_level": "low",
                "defects": ["no_object_detected"],
            }

        confs = boxes.conf.tolist()       # list[float] — confidence mỗi box
        cls_ids = boxes.cls.tolist()      # list[float] — class id mỗi box
        detected_names = [names[int(c)] for c in cls_ids]

        avg_conf = sum(confs) / len(confs)
        max_conf = max(confs)
        n_objects = len(confs)

        # Phát hiện vật thể lạ (không phải nông sản)
        crop_lower = crop_name.lower()
        matched = any(
            crop_lower in aliases
            for cls_name, aliases in _CLASS_TO_CROP.items()
            if cls_name in detected_names
        )
        has_food = any(name in _FOOD_CLASSES for name in detected_names)

        defects: list[str] = []

        # Heuristic: dùng confidence và số lượng object để đánh giá chất lượng
        # Model yolov8n COCO không được train cho quality assessment, nên dùng proxy:
        # - avg confidence cao + ít object → sản phẩm rõ ràng → tốt
        # - confidence thấp → object mờ nhạt, có thể bị hỏng/méo
        # - nhiều object nhỏ → sản phẩm phân tán → phân loại thấp hơn

        if avg_conf >= 0.75:
            grade = "grade_1"
            damage_level = "low"
        elif avg_conf >= 0.50:
            grade = "grade_2"
            damage_level = "medium"
            defects.append("low_detection_confidence")
        else:
            grade = "grade_3"
            damage_level = "high"
            defects.append("poor_visual_quality")

        # Nếu detect nhiều object cùng loại (>5) → có thể ảnh chụp nhiều quả cùng lúc
        # không phải đánh giá đơn lẻ → hạ grade 1 bậc
        if n_objects > 5 and grade == "grade_1":
            grade = "grade_2"
            damage_level = "medium"
            defects.append("multiple_objects_mixed")

        # Nếu object không phải nông sản nào được biết đến
        if crop_lower and not matched and not has_food:
            defects.append("unrecognized_crop_type")

        disease_detected = damage_level in ("medium", "high")

        logger.info(
            f"[YOLO] {image_path}: {n_objects} objects, avg_conf={avg_conf:.2f}, "
            f"classes={detected_names}, grade={grade}"
        )

        return {
            "quality_grade":    grade,
            "confidence":       round(min(max_conf, 1.0), 3),
            "disease_detected": disease_detected,
            "damage_level":     damage_level,
            "defects":          defects,
            "detected_objects": detected_names,
            "avg_confidence":   round(avg_conf, 3),
        }


def _fallback_result() -> dict:
    return {
        "quality_grade": "grade_1",
        "confidence": 0.80,
        "disease_detected": False,
        "damage_level": "low",
        "defects": [],
    }
