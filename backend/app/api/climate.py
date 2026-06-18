from fastapi import APIRouter
from app.services.climate_service import get_weather

router = APIRouter()


@router.get("/current")
def current_weather(city: str = "Delhi"):
    return get_weather(city)