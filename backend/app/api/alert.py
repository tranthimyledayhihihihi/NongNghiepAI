from fastapi import APIRouter

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# Alert endpoints will be implemented in Phase 2

@router.get("/")
async def get_alerts():
    """Get user alerts - Phase 2"""
    return {
        "message": "Alert feature coming in Phase 2",
        "alerts": []
    }

@router.post("/subscribe")
async def subscribe_alert():
    """Subscribe to price alerts - Phase 2"""
    return {
        "message": "Alert subscription feature coming in Phase 2",
        "status": "pending"
    }
