import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import stream, reports, alerts
from app.modules.reporter import start_background_reporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Dog Monitor backend...")
    task = asyncio.create_task(start_background_reporter())
    yield
    task.cancel()
    logger.info("Shutting down Dog Monitor backend.")


app = FastAPI(title="Dog Monitor API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stream.router)
app.include_router(reports.router)
app.include_router(alerts.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "dog-monitor"}
