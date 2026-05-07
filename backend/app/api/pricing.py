import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.price_schema import (
    PriceForecastRequest,
    PriceForecastResponse,
    PriceImportItem,
    PriceImportRequest,
    PriceImportResponse,
    PriceRequest,
    PriceResponse,
    PricingSuggestRequest,
    PricingSuggestResponse,
)
from app.services.pricing_service import pricing_service
from app.tasks.price_tasks import refresh_market_prices_task

router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@router.post("/current", response_model=PriceResponse)
async def get_current_price(request: PriceRequest, db: Session = Depends(get_db)):
    return pricing_service.get_current_price(
        db,
        request.crop_name,
        request.region,
        request.quality_grade,
    )


@router.get("/current", response_model=PriceResponse)
async def get_current_price_query(
    crop_name: str,
    region: str,
    quality_grade: str = "grade_1",
    db: Session = Depends(get_db),
):
    return pricing_service.get_current_price(db, crop_name, region, quality_grade)


@router.post("/suggest", response_model=PricingSuggestResponse)
async def suggest_price(request: PricingSuggestRequest, db: Session = Depends(get_db)):
    return pricing_service.suggest_price(db, request)


@router.post("/forecast", response_model=PriceForecastResponse)
async def forecast_price(request: PriceForecastRequest):
    return pricing_service.forecast_price(request.crop_name, request.region, request.days)


@router.get("/history/{crop_name}/{region}")
async def get_price_history(crop_name: str, region: str, days: int = 30, db: Session = Depends(get_db)):
    return {
        "crop_name": crop_name,
        "region": region,
        "history": pricing_service.get_price_history(db, crop_name, region, days),
    }


@router.post("/import", response_model=PriceImportResponse)
async def import_prices(request: PriceImportRequest, db: Session = Depends(get_db)):
    return pricing_service.import_prices(db, request.records)


@router.post("/import-csv", response_model=PriceImportResponse)
async def import_prices_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from exc

    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        try:
            records.append(
                PriceImportItem(
                    crop_name=row.get("crop_name") or row.get("crop") or row.get("CropName"),
                    region=row.get("region") or row.get("Region"),
                    price=float(row.get("price") or row.get("price_per_kg") or row.get("PricePerKg")),
                    quality_grade=row.get("quality_grade") or row.get("QualityGrade") or "grade_1",
                    source_name=row.get("source_name") or row.get("SourceName") or "manual_csv",
                    source_url=row.get("source_url") or row.get("SourceURL") or None,
                    price_date=row.get("price_date") or row.get("PriceDate") or None,
                    market_type=row.get("market_type") or row.get("MarketType") or None,
                )
            )
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=f"Invalid CSV row: {row}") from exc

    return pricing_service.import_prices(db, records)


@router.post("/refresh")
async def refresh_market_prices(source_name: str | None = None, crop_filter: str | None = None):
    return refresh_market_prices_task(source_name=source_name, crop_filter=crop_filter)


@router.get("/compare-regions/{crop_name}")
async def compare_regions(crop_name: str, region: str = "Ha Noi", db: Session = Depends(get_db)):
    suggestion = pricing_service.suggest_price(
        db,
        PricingSuggestRequest(
            crop_name=crop_name,
            region=region,
            quantity=1,
            quality_grade="grade_1",
        ),
    )
    return {"crop_name": crop_name, "regions": suggestion["nearby_region_prices"]}
