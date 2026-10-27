from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.modules.camera import mjpeg_generator

router = APIRouter(tags=["stream"])


@router.get("/video-stream")
async def video_stream():
    """MJPEG live stream from Tapo C211."""
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
