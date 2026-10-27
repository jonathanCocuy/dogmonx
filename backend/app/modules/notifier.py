import logging
import httpx
import cv2
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
ALERTS_DIR = Path("data/alerts")
ALERTS_DIR.mkdir(parents=True, exist_ok=True)

_push_tokens: set[str] = set()


def register_token(token: str):
    _push_tokens.add(token)
    logger.info("Push token registered (%d total)", len(_push_tokens))


def get_tokens() -> list[str]:
    return list(_push_tokens)


def save_alert_image(frame: np.ndarray, alert_id: str) -> str:
    """Saves frame as JPEG and returns the filename."""
    path = ALERTS_DIR / f"{alert_id}.jpg"
    cv2.imwrite(str(path), frame)
    return str(path)


async def send_push_notification(title: str, body: str, alert_id: str, api_url: str):
    """Sends push notification to all registered devices via Expo."""
    if not _push_tokens:
        logger.debug("No push tokens registered, skipping notification")
        return

    image_url = f"{api_url}/alert-image/{alert_id}"
    messages = [
        {
            "to": token,
            "title": title,
            "body": body,
            "data": {"alert_id": alert_id, "image_url": image_url},
            "sound": "default",
            "priority": "high",
        }
        for token in _push_tokens
    ]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                EXPO_PUSH_URL,
                json=messages,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
            resp.raise_for_status()
            logger.info("Push notification sent to %d device(s): %s", len(_push_tokens), title)
    except Exception as exc:
        logger.error("Failed to send push notification: %s", exc)
