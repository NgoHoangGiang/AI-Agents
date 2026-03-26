from fastapi import FastAPI

from app.config import settings
from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router
from app.routes.health import router as health_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.app_debug,
)


@app.get("/")
def root() -> dict:
    return {
        "message": f"{settings.app_name} is running",
        "environment": settings.app_env,
        "version": settings.app_version,
    }


app.include_router(health_router)
app.include_router(documents_router)
app.include_router(chat_router)