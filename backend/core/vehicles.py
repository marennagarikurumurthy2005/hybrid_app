VEHICLE_TYPES = ["BIKE", "AUTO", "CAR", "SUV"]

VEHICLE_RATES_PER_KM = {
    "BIKE": 8,
    "AUTO": 12,
    "CAR": 18,
    "SUV": 25,
}


def normalize_vehicle_type(value):
    if value is None:
        return None
    cleaned = str(value).strip().upper()
    if cleaned in VEHICLE_RATES_PER_KM:
        return cleaned
    return None


def get_vehicle_rate(vehicle_type):
    normalized = normalize_vehicle_type(vehicle_type)
    if not normalized:
        return None
    return VEHICLE_RATES_PER_KM[normalized]
