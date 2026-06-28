from typing import List, Dict
from math import radians, cos, sin, sqrt, atan2


def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371000
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def classify_surface(index: int):
    options = [
        ("asphalt", 3.0),
        ("paved", 4.0),
        ("concrete", 3.5),
        ("gravel", 10.0),
        ("unpaved", 11.0),
    ]
    return options[index % len(options)]


def simplify_coordinates(coordinates: List[List[float]], max_points: int = 18):
    if len(coordinates) <= max_points:
        return coordinates

    step = max(1, len(coordinates) // max_points)
    simplified = coordinates[::step]

    if simplified[-1] != coordinates[-1]:
        simplified.append(coordinates[-1])

    return simplified


async def get_pavement_data(coordinates: List[List[float]]) -> List[Dict]:
    simplified = simplify_coordinates(coordinates)

    segments = []

    for i in range(len(simplified) - 1):
        start = simplified[i]
        end = simplified[i + 1]

        surface, iri = classify_surface(i)

        segments.append({
            "surface": surface,
            "smoothness": "estimado",
            "iri": iri,
            "start": start,
            "end": end,
            "distance": haversine_distance(start[1], start[0], end[1], end[0])
        })

    return segments