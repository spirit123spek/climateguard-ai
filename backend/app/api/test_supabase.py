from fastapi import APIRouter
from app.services.supabase_service import supabase

router = APIRouter()

@router.get("/supabase-test")
def supabase_test():

    result = (
        supabase
        .table("climate_readings")
        .select("*")
        .limit(1)
        .execute()
    )

    return {
        "status": "connected",
        "data": result.data
    }