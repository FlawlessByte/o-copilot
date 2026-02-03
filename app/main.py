from fastapi import FastAPI
import structlog

from app.config import get_settings
from app.logging_config import configure_structlog
from app.routes.usage import router as usage_router

app = FastAPI(title="Orbital Copilot Usage API")

settings = get_settings()

configure_structlog(settings.log_level)
logger = structlog.get_logger("o-copilot")


@app.get("/health")
def health():
    logger.debug("health_check invoked")
    return {"status": "ok"}

# Moved to separate section under /routes for readability
# GET /usage
app.include_router(usage_router)
