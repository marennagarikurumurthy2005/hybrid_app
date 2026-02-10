VEHICLE_TYPES = ["BIKE_PETROL", "BIKE_EV", "AUTO", "CAR", "SUV"]

VEHICLE_RATES_PER_KM = {
    "BIKE_PETROL": 8,
    "BIKE_EV": 8,
    "AUTO": 12,
    "CAR": 18,
    "SUV": 25,
}


def normalize_vehicle_type(value):
    if value is None:
        return None
    cleaned = str(value).strip().upper()
    if cleaned == "BIKE":
        cleaned = "BIKE_PETROL"
    if cleaned in VEHICLE_RATES_PER_KM:
        return cleaned
    return None


def get_vehicle_rate(vehicle_type):
    normalized = normalize_vehicle_type(vehicle_type)
    if not normalized:
        return None
    return VEHICLE_RATES_PER_KM[normalized]


def is_ev_vehicle(vehicle_type):
    normalized = normalize_vehicle_type(vehicle_type)
    return normalized == "BIKE_EV"
