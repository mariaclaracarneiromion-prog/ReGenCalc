from typing import List, Dict


FERREIRA_ENERGY_KJ_PER_100KM = {
    "boa": 2.7,
    "media": 19.75,
    "pobre": 1707.11
}


def classify_road_by_iri(iri: float) -> str:
    if iri <= 4:
        return "boa"
    if iri <= 9:
        return "media"
    return "pobre"


def calculate_energy_ferreira_2013(
    segments: List[Dict],
    vehicle_type: str,
    average_speed_ms: float
) -> Dict:
    total_energy_kj = 0
    road_classes = {"boa": 0, "media": 0, "pobre": 0}

    for segment in segments:
        iri = segment["iri"]
        distance_km = segment["distance"] / 1000

        road_class = classify_road_by_iri(iri)
        road_classes[road_class] += distance_km

        energy_kj_per_100km = FERREIRA_ENERGY_KJ_PER_100KM[road_class]
        total_energy_kj += energy_kj_per_100km * (distance_km / 100)

    energy_wh = total_energy_kj / 3.6
    dominant_class = max(road_classes, key=road_classes.get)

    return {
        "method_name": "Ferreira (2013) - Acumulador hidráulico de 5 L",
        "energy_wh": round(energy_wh, 3),
        "description": (
            f"Modelo baseado na dissertação de Ferreira (2013), usando a energia estimada "
            f"por 100 km para estrada boa, média ou pobre. Estrada predominante: {dominant_class}."
        )
    }


def generate_comparisons(energy_wh: float) -> Dict:
    return {
        "phone_charges": {"value": round(energy_wh / 15, 2), "description": "Cargas de celular"},
        "led_lamp_hours": {"value": round(energy_wh / 10, 2), "description": "Horas de lâmpada LED 10 W"},
        "notebook_hours": {"value": round(energy_wh / 50, 2), "description": "Horas de notebook"},
        "tv_hours": {"value": round(energy_wh / 40, 2), "description": "Horas de TV LED"},
        "fan_hours": {"value": round(energy_wh / 60, 2), "description": "Horas de ventilador"},
        "router_hours": {"value": round(energy_wh / 10, 2), "description": "Horas de roteador Wi-Fi"}
    }