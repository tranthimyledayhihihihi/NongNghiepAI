import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.integrations.claude_client import ai_client
from app.models.conversation import AIConversation
from app.services.pricing_service import pricing_service
from app.services.weather_service import weather_service


class ClaudeService:
    def answer_question(
        self,
        db: Session,
        *,
        question: str,
        user_id: int | None = None,
        crop_name: str | None = None,
        region: str | None = None,
        session_id: str | None = None,
    ) -> dict:
        context = self._build_context(db, crop_name=crop_name, region=region, user_id=user_id)
        system_prompt = (
            "You are AgriBot for a Vietnamese agriculture support system. "
            "Answer in Vietnamese, be practical, cite the provided system context, "
            "and clearly say when data is missing or demo fallback is used."
        )
        user_prompt = f"Context JSON:\n{json.dumps(context, ensure_ascii=False, default=str)}\n\nQuestion: {question}"
        try:
            completion = ai_client.complete([{"role": "user", "content": user_prompt}], system_prompt=system_prompt)
        except Exception as exc:
            completion = {
                "answer": self._fallback_answer(question, context, str(exc)),
                "provider": "rule_based_fallback",
                "model": "local-context-v1",
                "token_usage": None,
                "is_mock": True,
                "error": str(exc),
            }

        self._save_conversation(db, user_id, session_id, question, completion, context, crop_name)
        return {
            "answer": completion["answer"],
            "provider": completion["provider"],
            "model": completion["model"],
            "token_usage": completion.get("token_usage"),
            "context": context,
            "is_mock": completion.get("is_mock", False),
            "error": completion.get("error"),
            "created_at": datetime.now(),
        }

    def get_market_insights(self, crop_name: str, region: str) -> str:
        return f"Hay goi /api/ai/chat voi crop_name={crop_name}, region={region} de lay insight co context."

    def get_selling_recommendations(self, data: dict) -> str:
        return "Dung /api/market/suggest va /api/ai/chat de lay khuyen nghi co du lieu gia/thoi tiet."

    def _build_context(self, db: Session, crop_name: str | None, region: str | None, user_id: int | None) -> dict:
        region = region or "Ha Noi"
        context: dict = {"region": region}
        if crop_name:
            context["crop_name"] = crop_name
            context["pricing"] = pricing_service.get_current_price(db, crop_name, region)
            context["price_history"] = pricing_service.get_price_history(db, crop_name, region, 14)
        context["weather"] = weather_service.get_current_weather(db, region)
        context["weather_forecast"] = weather_service.get_forecast(db, region, 7)
        if user_id:
            context["recent_quality_records"] = self._recent_quality_records(db, user_id)
            context["harvest_schedules"] = self._active_harvest_schedules(db, user_id)
        return context

    @staticmethod
    def _recent_quality_records(db: Session, user_id: int) -> list[dict]:
        try:
            from app.models.quality import QualityRecord

            rows = db.query(QualityRecord).filter(QualityRecord.UserID == user_id).order_by(QualityRecord.CheckDate.desc()).limit(5).all()
            return [
                {
                    "quality_grade": row.AIGrade,
                    "confidence": row.ConfidenceScore,
                    "checked_at": row.CheckDate,
                    "issues": row.DetectedIssues,
                }
                for row in rows
            ]
        except Exception:
            return []

    @staticmethod
    def _active_harvest_schedules(db: Session, user_id: int) -> list[dict]:
        try:
            from app.models.harvest import HarvestSchedule

            rows = db.query(HarvestSchedule).filter(HarvestSchedule.UserID == user_id).order_by(HarvestSchedule.CreatedAt.desc()).limit(5).all()
            return [
                {
                    "crop_id": row.CropID,
                    "region": row.Region,
                    "planting_date": row.PlantingDate,
                    "expected_harvest_date": row.ExpectedHarvestDate,
                    "status": row.Status,
                }
                for row in rows
            ]
        except Exception:
            return []

    @staticmethod
    def _fallback_answer(question: str, context: dict, error: str) -> str:
        parts = [
            "He thong chua goi duoc AI provider nen day la cau tra loi fallback dua tren du lieu noi bo.",
            f"Ly do provider: {error}",
        ]
        pricing = context.get("pricing")
        if pricing:
            parts.append(
                f"Gia hien tai {pricing.get('crop_name')} tai {pricing.get('region')} la "
                f"{pricing.get('current_price'):,.0f} VND/kg, nguon {pricing.get('source_name')}."
            )
        weather = context.get("weather")
        if weather:
            parts.append(
                f"Thoi tiet {weather.get('region')}: {weather.get('temperature')}C, "
                f"mua {weather.get('rainfall')}mm, nguon {weather.get('source_name')}."
            )
        parts.append("Hay cau hinh CLAUDE_API_KEY hoac AI_PROVIDER=openai + AI_API_KEY de co tra loi AI that.")
        return "\n".join(parts)

    @staticmethod
    def _save_conversation(
        db: Session,
        user_id: int | None,
        session_id: str | None,
        question: str,
        completion: dict,
        context: dict,
        crop_name: str | None,
    ) -> None:
        try:
            related_crop_id = None
            if crop_name:
                from app.models.crop import Crop

                crop = db.query(Crop).filter(Crop.CropName == crop_name).first()
                related_crop_id = crop.CropID if crop else None
            row = AIConversation(
                UserID=user_id,
                SessionID=session_id,
                UserMessage=question,
                AIResponse=completion["answer"],
                Topic="agriculture",
                RelatedCropID=related_crop_id,
                ContextSnapshot=json.dumps(context, ensure_ascii=False, default=str),
                Provider=completion.get("provider"),
                ModelName=completion.get("model"),
                TokenUsage=json.dumps(completion.get("token_usage"), ensure_ascii=False),
            )
            db.add(row)
            db.commit()
        except Exception:
            db.rollback()


claude_service = ClaudeService()
