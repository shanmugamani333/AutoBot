import structlog
from fastapi import APIRouter, Request, HTTPException
from api.config import get_settings

router = APIRouter()
logger = structlog.get_logger()
settings = get_settings()


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Receives Telegram updates.
    Week 1: just log and acknowledge.
    Week 2: full intent routing added here.
    """
    try:
        body = await request.json()
        logger.info("webhook_received", update_id=body.get("update_id"))

        # TODO Week 2: route through intent classifier
        return {"ok": True}

    except Exception as e:
        logger.error("webhook_error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal error")
