# Celery app configuration for scheduled tasks
from celery import Celery
from celery.schedules import crontab
import os

# Create Celery app
app = Celery(
    'agri_crawler',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Ho_Chi_Minh',
    enable_utc=True,
)

# Scheduled tasks
app.conf.beat_schedule = {
    'crawl-agro-daily': {
        'task': 'crawler.tasks.scheduled_tasks.crawl_agro',
        'schedule': crontab(hour=6, minute=0),  # Run at 6:00 AM daily
    },
    'crawl-giavn-daily': {
        'task': 'crawler.tasks.scheduled_tasks.crawl_giavn',
        'schedule': crontab(hour=7, minute=0),  # Run at 7:00 AM daily
    },
    'update-price-history': {
        'task': 'crawler.tasks.scheduled_tasks.update_price_history',
        'schedule': crontab(hour=23, minute=0),  # Run at 11:00 PM daily
    },
}

if __name__ == '__main__':
    app.start()
