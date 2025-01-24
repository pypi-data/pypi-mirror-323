import random
from datetime import datetime

def get_currentLocation(launch_time, angle, latitude, longitude):
    latitude = round(random.uniform(-90, 90), 4)  # 랜덤 위도 (-90 ~ 90)
    longitude = round(random.uniform(-180, 180), 4)  # 랜덤 경도 (-180 ~ 180)
    altitude = random.randint(200, 1000)  # 랜덤 고도 (200 ~ 1000)
    satellite_id = random.randint(0, 99999)  # 랜덤 위성 ID (0 ~ 99999)
    timestamp = datetime.utcnow().isoformat() + "Z"  # 현재 UTC 타임스탬프

    return {
        "satellite_position": {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude
        },
        "satellite_id": satellite_id,
        "timestamp": timestamp
    }

def how_are_you():
    return "fine thankYou and you"

