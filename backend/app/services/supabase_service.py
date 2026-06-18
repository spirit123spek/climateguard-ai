from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("SERVICE KEY LOADED:", SUPABASE_SERVICE_ROLE_KEY is not None)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)


def save_climate_reading(data):
    return (
        supabase
        .table("climate_readings")
        .insert(data)
        .execute()
    )

def save_prediction(data):

    return (
        supabase
        .table("predictions")
        .insert(data)
        .execute()
    )