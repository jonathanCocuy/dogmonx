import asyncio
import json
import logging
import os
from datetime import datetime, date
from pathlib import Path
import cv2
import numpy as np
from app.modules.camera import capture_frame
from app.modules.detector import detect_dogs
from app.modules.ai_reporter import generate_report
from app.modules.notifier import send_push_notification, save_alert_image

logger = logging.getLogger(__name__)

REPORT_INTERVAL = int(os.getenv("REPORT_INTERVAL_SECONDS", "30"))
MOTION_ALERT_THRESHOLD = float(os.getenv("MOTION_ALERT_THRESHOLD", "0.04"))
PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

_latest_report: dict = {}
_history: list[dict] = []


def _compute_motion(frames: list) -> float:
    """Mean normalised pixel diff between consecutive frames — real motion metric."""
    if len(frames) < 2:
        return 0.0
    diffs = []
    for i in range(len(frames) - 1):
        g1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        g2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
        diffs.append(float(np.mean(cv2.absdiff(g1, g2))) / 255.0)
    return round(float(np.mean(diffs)), 3)


def _build_montage(frames: list) -> np.ndarray:
    """Creates a 2x2 grid from up to 4 frames so the AI sees temporal context."""
    h, w = 360, 640
    resized = [cv2.resize(f, (w, h)) for f in frames[:4]]
    while len(resized) < 4:
        resized.append(np.zeros((h, w, 3), dtype=np.uint8))
    # Add frame number label
    for i, img in enumerate(resized):
        label = f"t+{i}s"
        cv2.putText(img, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    top = np.hstack([resized[0], resized[1]])
    bot = np.hstack([resized[2], resized[3]])
    return np.vstack([top, bot])


def get_latest_report() -> dict:
    return _latest_report


def get_history() -> list[dict]:
    today = date.today().isoformat()
    return [r for r in _history if r.get("date") == today]


def _history_file() -> Path:
    return DATA_DIR / f"reports_{date.today().isoformat()}.json"


def _load_today_history():
    global _history
    path = _history_file()
    if path.exists():
        with open(path) as f:
            _history = json.load(f)
    else:
        _history = []


def _save_report(report: dict):
    global _history, _latest_report
    _latest_report = report
    _history.append(report)
    with open(_history_file(), "w") as f:
        json.dump(_history, f, ensure_ascii=False, indent=2)


async def start_background_reporter():
    """Long-running task: captures frames, detects dogs, generates AI report."""
    logger.info("Background reporter started (interval=%ds)", REPORT_INTERVAL)
    _load_today_history()
    while True:
        try:
            # Capture 4 frames spaced 1s apart for motion context
            frames = []
            for i in range(4):
                f = await asyncio.to_thread(capture_frame)
                if f is not None:
                    frames.append(f)
                if i < 3:
                    await asyncio.sleep(1)

            if not frames:
                logger.warning("No frames captured, skipping cycle")
                await asyncio.sleep(REPORT_INTERVAL)
                continue

            # Real motion: mean pixel diff between consecutive frames
            motion_score = _compute_motion(frames)

            # Use last frame for YOLO detection
            frame = frames[-1]
            detection = await asyncio.to_thread(detect_dogs, frame)
            detection["motion_score"] = motion_score

            description = await generate_report(frame, detection)

            report = {
                "timestamp": datetime.now().isoformat(),
                "date": date.today().isoformat(),
                "description": description,
                "dogs_count": detection["dogs_count"],
                "motion_score": detection["motion_score"],
                "other_objects": detection["other_objects"],
            }
            _save_report(report)
            logger.info("Report saved: %s", description)

            if detection["motion_score"] > MOTION_ALERT_THRESHOLD:
                alert_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_alert_image(frame, alert_id)
                dogs = detection["dogs_count"]
                title = "🐕 Actividad detectada"
                if dogs == 0:
                    title = "👀 Movimiento detectado"
                elif dogs == 1:
                    title = "🐕 Tu perro se está moviendo"
                await send_push_notification(title, description, alert_id, PUBLIC_API_URL)
                logger.info("Alert sent (motion=%.2f)", detection["motion_score"])

        except Exception as exc:
            msg = str(exc)
            if "Invalid authentication" in msg:
                logger.error("AUTH ERROR: Credenciales incorrectas en .env — corregí TAPO_USER y TAPO_PASSWORD y reiniciá el backend. Deteniendo reintentos.")
                return  # stop loop to avoid camera suspension
            if "Temporary Suspension" in msg:
                wait = 600
                logger.warning("Cámara suspendida. Esperando %ds antes de reintentar...", wait)
                await asyncio.sleep(wait)
                continue
            logger.error("Error in reporter cycle: %s", exc, exc_info=True)

        await asyncio.sleep(REPORT_INTERVAL)
