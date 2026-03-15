from fastapi import FastAPI
from app.routers import items
from app.config import Settings

settings = Settings()

app = FastAPI(title=settings.app_name)

app.include_router(items.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/info")
def get_info():
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_page": settings.items_per_page
    }