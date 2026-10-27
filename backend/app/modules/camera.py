import asyncio
import logging
import os
from typing import AsyncGenerator, Optional
import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TAPO_IP = os.getenv("TAPO_IP", "192.168.1.100")
TAPO_USER = os.getenv("TAPO_USER", "")
TAPO_PASSWORD = os.getenv("TAPO_PASSWORD", "")

# Tapo C211 RTSP URLs (no pytapo needed — standard RTSP auth)
# stream1 = main HD stream, stream2 = sub stream (lower res, faster)
def _rtsp_url(stream: int = 1) -> str:
    from urllib.parse import quote
    user = quote(TAPO_USER, safe="")
    pwd = quote(TAPO_PASSWORD, safe="")
    return f"rtsp://{user}:{pwd}@{TAPO_IP}:554/stream{stream}"


def capture_frame() -> Optional[np.ndarray]:
    """Captures a single frame from the camera via RTSP."""
    url = _rtsp_url(2)  # use substream for snapshots (faster)
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    try:
        ret, frame = cap.read()
        if not ret:
            logger.warning("Failed to read frame — check RTSP credentials/IP")
            return None
        logger.debug("Frame captured OK (%dx%d)", frame.shape[1], frame.shape[0])
        return frame
    finally:
        cap.release()


async def mjpeg_generator() -> AsyncGenerator[bytes, None]:
    """Yields MJPEG frames for the /video-stream endpoint."""
    url = _rtsp_url(1)  # main stream for live view
    logger.info("MJPEG stream starting (RTSP direct)")
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Stream read failed, retrying in 2s")
                await asyncio.sleep(2)
                cap.release()
                cap = cv2.VideoCapture(url)
                continue
            _, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"
            )
            await asyncio.sleep(0.033)
    finally:
        cap.release()
        logger.info("MJPEG stream stopped")
