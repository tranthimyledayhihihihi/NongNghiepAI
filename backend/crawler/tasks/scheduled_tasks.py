"""P2-16: Celery Scheduled Tasks"""
import os, sys, logging, subprocess
from datetime import datetime, date
from celery import shared_task

logger = logging.getLogger(__name__)


def _get_db():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from app.core.database import SessionLocal
    return SessionLocal()


def _run_spider(name):
    crawler_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    r = subprocess.run(
        ["scrapy", "crawl", name, "--logfile", f"/tmp/{name}.log"],
        cwd=crawler_dir, capture_output=True, text=True, timeout=300
    )
    return {"status": "success" if r.returncode == 0 else "error", "spider": name}


@shared_task(bind=True, max_retries=2)
def crawl_agro(self):
    try:
        return _run_spider("agro")
    except Exception as e:
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=2)
def crawl_giavn(self):
    try:
        return _run_spider("giavn")
    except Exception as e:
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=2)
def crawl_nongnghiep(self):
    try:
        return _run_spider("nongnghiep")
    except Exception as e:
        raise self.retry(exc=e, countdown=60)


@shared_task
def update_price_history():
    db = None
    try:
        db = _get_db()
        from app.models.price import MarketPrice, PriceHistory
        from sqlalchemy import func
        today = date.today()
        rows = (
            db.query(
                MarketPrice.CropID, MarketPrice.Region,
                func.avg(MarketPrice.PricePerKg).label("avg"),
                func.min(MarketPrice.PricePerKg).label("mn"),
                func.max(MarketPrice.PricePerKg).label("mx"),
                func.count().label("vol"),
            )
            .filter(MarketPrice.PriceDate == today)
            .group_by(MarketPrice.CropID, MarketPrice.Region)
            .all()
        )
        saved = 0
        for row in rows:
            ex = db.query(PriceHistory).filter(
                PriceHistory.CropID == row.CropID,
                PriceHistory.Region == row.Region,
                PriceHistory.RecordDate == today
            ).first()
            if ex:
                ex.AvgPrice = row.avg
                ex.MinPrice = row.mn
                ex.MaxPrice = row.mx
                ex.Volume = float(row.vol)
            else:
                db.add(PriceHistory(CropID=row.CropID, Region=row.Region,
                                    AvgPrice=row.avg, MinPrice=row.mn, MaxPrice=row.mx,
                                    Volume=float(row.vol), RecordDate=today))
            saved += 1
        db.commit()
        return {"status": "success", "records": saved}
    except Exception as e:
        logger.error(f"update_price_history: {e}")
        if db: db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if db: db.close()


@shared_task
def check_price_alerts():
    db = None
    try:
        db = _get_db()
        from app.services.alert_service import alert_service
        triggered = alert_service.check_and_trigger_alerts(db)
        return {"status": "success", "triggered": len(triggered)}
    except Exception as e:
        logger.error(f"check_price_alerts: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if db: db.close()


@shared_task
def precompute_price_forecasts():
    TOP_CROPS = ["Ca chua", "Dua chuot", "Ot", "Khoai lang", "Sau rieng", "Lua"]
    TOP_REGIONS = ["Ha Noi", "TP.HCM", "Lam Dong", "Can Tho"]
    db = None
    computed = 0
    try:
        db = _get_db()
        from app.services.price_forecast_service import price_forecast_service
        for crop in TOP_CROPS:
            for region in TOP_REGIONS:
                try:
                    price_forecast_service.predict_price(db, crop, region, 7)
                    computed += 1
                except Exception:
                    pass
        return {"status": "success", "computed": computed}
    except Exception as e:
        logger.error(f"precompute_price_forecasts: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if db: db.close()
