import httpx
from typing import Dict, Any


async def get_route(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> Dict[str, Any]:
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
    )

    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "false"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if data.get("code") != "Ok":
        raise ValueError("Não foi possível calcular a rota.")

    route = data["routes"][0]

    return {
        "distance": route["distance"],
        "duration": route["duration"],
        "geometry": route["geometry"]
    }