def calculate_prediction(climate_data):

    aqi = climate_data.get("aqi", 0) or 0
    temperature = climate_data.get("temperature", 0) or 0
    humidity = climate_data.get("humidity", 0) or 0

    risk_score = (
        (aqi * 0.5)
        + (temperature * 0.3)
        + (humidity * 0.2)
    )

    risk_score = round(min(risk_score, 100), 2)

    if risk_score < 35:
        risk_level = "Low"
    elif risk_score < 70:
        risk_level = "Medium"
    else:
        risk_level = "High"

    esg_score = round(100 - risk_score, 2)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "esg_score": esg_score
    }