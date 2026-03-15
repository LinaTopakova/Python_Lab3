import logging
from fastapi import FastAPI
from app.routers import items
from app.config import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

settings = Settings()

app = FastAPI(
    title=settings.app_name,
    description="Лабораторная работа по FastAPI - изучение основных возможностей фреймворка",
    version="1.0.0",
    contact={
        "name": "Студент",
        "email": settings.admin_email,
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.include_router(items.router)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello, FastAPI!"}

@app.get("/info")
def get_info():
    logger.debug("Info endpoint accessed")
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_page": settings.items_per_page
    }

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response