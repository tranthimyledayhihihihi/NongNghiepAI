from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import os

class QualityDetector:
    def __init__(self, model_path: str = "backend/ai_models/weights/best.pt"):
        """Initialize YOLO model for quality detection"""
        self.model_path = model_path
        self.model = None
        self.load_model()
        
        # Quality grading thresholds
        self.quality_thresholds = {
            'grade_1': {'max_defects': 0, 'min_confidence': 0.8},
            'grade_2': {'max_defects': 2, 'min_confidence': 0.6},
            'grade_3': {'max_defects': 5, 'min_confidence': 0.4}
        }
    
    def load_model(self):
        """Load YOLO model"""
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                print(f"✓ Loaded YOLO model from {self.model_path}")
            else:
                # Use pretrained model as fallback
                print(f"⚠ Model not found at {self.model_path}, using YOLOv8n")
                self.model = YOLO('yolov8n.pt')
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            self.model = None
    
    def detect_defects(self, image_path: str) -> Dict:
        """Detect defects in agricultural product image"""
        if self.model is None:
            return self._mock_detection()
        
        try:
            # Run inference
            results = self.model(image_path, conf=0.25)
            
            defects = []
            confidences = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = result.names[cls]
                    
                    defects.append(class_name)
                    confidences.append(conf)
            
            return {
                'defects': defects,
                'defect_count': len(defects),
                'confidences': confidences,
                'avg_confidence': np.mean(confidences) if confidences else 0.0
            }
        except Exception as e:
            print(f"Detection error: {e}")
            return self._mock_detection()
    
    def grade_quality(self, detection_result: Dict) -> Tuple[str, float]:
        """Grade quality based on detection results"""
        defect_count = detection_result['defect_count']
        avg_confidence = detection_result['avg_confidence']
        
        if defect_count == 0 and avg_confidence > 0.8:
            return 'grade_1', 0.95
        elif defect_count <= 2 and avg_confidence > 0.6:
            return 'grade_2', 0.75
        else:
            return 'grade_3', 0.55
    
    def analyze_image(self, image_path: str) -> Dict:
        """Complete analysis of product image"""
        detection = self.detect_defects(image_path)
        grade, confidence = self.grade_quality(detection)
        
        # Price suggestions based on grade
        price_ranges = {
            'grade_1': {'min': 25000, 'max': 35000},
            'grade_2': {'min': 15000, 'max': 24000},
            'grade_3': {'min': 8000, 'max': 14000}
        }
        
        recommendations = self._get_recommendations(grade, detection['defects'])
        
        return {
            'quality_grade': grade,
            'confidence': confidence,
            'defects': detection['defects'],
            'defect_count': detection['defect_count'],
            'suggested_price_range': price_ranges[grade],
            'recommendations': recommendations
        }
    
    def _get_recommendations(self, grade: str, defects: List[str]) -> List[str]:
        """Get recommendations based on quality grade"""
        recommendations = []
        
        if grade == 'grade_1':
            recommendations.append("Chất lượng tốt - phù hợp xuất khẩu hoặc siêu thị cao cấp")
            recommendations.append("Nên bán sớm để giữ độ tươi")
        elif grade == 'grade_2':
            recommendations.append("Chất lượng trung bình - phù hợp chợ đầu mối")
            recommendations.append("Có thể bán cho thương lái địa phương")
        else:
            recommendations.append("Chất lượng thấp - nên bán nhanh")
            recommendations.append("Phù hợp chế biến hoặc bán giá rẻ")
        
        if defects:
            recommendations.append(f"Phát hiện: {', '.join(set(defects))}")
        
        return recommendations
    
    def _mock_detection(self) -> Dict:
        """Mock detection for testing without model"""
        return {
            'defects': [],
            'defect_count': 0,
            'confidences': [0.85],
            'avg_confidence': 0.85
        }

# Singleton instance
quality_detector = QualityDetector()
