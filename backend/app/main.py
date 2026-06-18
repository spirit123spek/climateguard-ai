from fastapi import FastAPI

from app.api.climate import router as climate_router
from app.api.test_supabase import router as test_router

app = FastAPI(
    title="ClimateGuard AI API",
    version="0.1.0",
    description="Backend foundation for ClimateGuard AI."
)

app.include_router(
    climate_router,
    prefix="/api/climate",
    tags=["Climate"]
)

app.include_router(
    test_router,
    prefix="/api/test",
    tags=["Testing"]
)