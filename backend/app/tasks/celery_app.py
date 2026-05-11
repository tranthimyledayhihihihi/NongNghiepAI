import os
from celery import Celery
from celery.schedules import crontab

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("agri_tasks", broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Ho_Chi_Minh',
    enable_utc=True,
)

# Cấu hình Celery Beat (Lập lịch tự động)
celery_app.conf.beat_schedule = {
    "crawl-prices-daily": {
        "task": "app.tasks.crawler_tasks.run_price_crawler",
        "schedule": crontab(hour=2, minute=0), # Chạy 2h sáng mỗi ngày
    },
    "check-price-alerts-hourly": {
        "task": "app.tasks.alert_tasks.check_active_alerts",
        "schedule": crontab(minute=0), # Chạy đầu mỗi giờ
    },
    "cleanup-uploads-weekly": {
        "task": "app.tasks.cleanup_tasks.cleanup_old_uploads",
        "schedule": crontab(day_of_week='sunday', hour=3, minute=0), # Chạy 3h sáng Chủ Nhật
    }
}