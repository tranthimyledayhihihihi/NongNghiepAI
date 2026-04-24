from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.quality_schema import QualityCheckResponse
# Sửa thành
from ai_models.yolo_inference import quality_detector
import shutil
from pathlib import Path
import uuid

router = APIRouter(prefix="/api/quality", tags=["quality"])

# Create upload directory
UPLOAD_DIR = Path("uploads/quality_check")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/check", response_model=QualityCheckResponse)
async def check_quality(file: UploadFile = File(...)):
    """
    Kiểm tra chất lượng nông sản qua ảnh
    
    - Upload ảnh nông sản
    - AI phân tích và phân loại chất lượng
    - Trả về kết quả và giá đề xuất
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File phải là ảnh")
    
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        file_path = UPLOAD_DIR / f"{file_id}{file_extension}"
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analyze image
        result = quality_detector.analyze_image(str(file_path))
        
        # Clean up
        file_path.unlink()
        
        return QualityCheckResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý ảnh: {str(e)}")

@router.get("/grades")
async def get_quality_grades():
    """Lấy danh sách các phân loại chất lượng"""
    return {
        "grades": [
            {
                "grade": "grade_1",
                "name": "Loại 1",
                "description": "Chất lượng cao, không khuyết tật",
                "price_multiplier": 1.0
            },
            {
                "grade": "grade_2",
                "name": "Loại 2",
                "description": "Chất lượng trung bình, ít khuyết tật",
                "price_multiplier": 0.7
            },
            {
                "grade": "grade_3",
                "name": "Loại 3",
                "description": "Chất lượng thấp, nhiều khuyết tật",
                "price_multiplier": 0.4
            }
        ]
    }