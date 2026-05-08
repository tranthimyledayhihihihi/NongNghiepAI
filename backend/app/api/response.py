from datetime import datetime
from typing import Any


def api_response(
    data: Any,
    *,
    source: str = "database",
    is_realtime: bool = False,
    is_mock: bool = False,
    cache_status: str = "from_db",
    last_updated: datetime | None = None,
    message: str = "OK",
) -> dict:
    return {
        "success": True,
        "data": data,
        "meta": {
            "source": source,
            "is_realtime": is_realtime,
            "is_mock": is_mock,
            "cache_status": cache_status,
            "last_updated": last_updated or datetime.now(),
        },
        "message": message,
    }
