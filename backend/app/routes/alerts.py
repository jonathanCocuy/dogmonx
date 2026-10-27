import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.modules.notifier import register_token, get_tokens, ALERTS_DIR

router = APIRouter(tags=["alerts"])

API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")


class TokenRequest(BaseModel):
    token: str


@router.post("/register-token")
async def register_push_token(req: TokenRequest):
    register_token(req.token)
    return {"status": "registered"}


@router.get("/alert-image/{alert_id}")
async def get_alert_image(alert_id: str):
    # Sanitize to prevent path traversal
    safe_id = alert_id.replace("/", "").replace("..", "")
    path = ALERTS_DIR / f"{safe_id}.jpg"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(path), media_type="image/jpeg")
