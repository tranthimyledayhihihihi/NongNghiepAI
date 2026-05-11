import os
import time
from app.tasks.celery_app import celery_app

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "storage/uploads")
MAX_AGE_DAYS = 7

@celery_app.task
def cleanup_old_uploads():
    """Xóa các file ảnh phân tích chất lượng đã quá cũ để giải phóng ổ cứng."""
    if not os.path.exists(UPLOAD_DIR):
        return
        
    current_time = time.time()
    deleted_count = 0
    
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            if (current_time - os.path.getctime(file_path)) > (MAX_AGE_DAYS * 86400):
                os.remove(file_path)
                deleted_count += 1
                
    return f"Deleted {deleted_count} old files."