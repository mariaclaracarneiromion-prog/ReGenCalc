import httpx
from typing import Tuple


async def geocode_address(address: str) -> Tuple[float, float]:
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address + ", Brasil",
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "ReGenCalc/1.0"
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

    if not data:
        raise ValueError(f"Endereço não encontrado: {address}")

    return float(data[0]["lat"]), float(data[0]["lon"])