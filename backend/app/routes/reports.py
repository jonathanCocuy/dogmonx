from fastapi import APIRouter
from app.modules.reporter import get_latest_report, get_history

router = APIRouter(tags=["reports"])


@router.get("/latest-report")
async def latest_report():
    """Returns the most recent AI-generated dog report."""
    report = get_latest_report()
    if not report:
        return {"message": "No report available yet. Wait up to 30 seconds."}
    return report


@router.get("/history")
async def history():
    """Returns all reports from today."""
    return {"reports": get_history(), "count": len(get_history())}
