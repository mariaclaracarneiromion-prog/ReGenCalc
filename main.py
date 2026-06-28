from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from models.schemas import RouteRequest, RouteResponse, Segment, EnergyResult
from services.geocoding import geocode_address
from services.routing import get_route
from services.pavement import get_pavement_data
from services.energy_calculation import (
    calculate_energy_ferreira_2013,
    generate_comparisons
)

BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title="ReGenCalc",
    description="Simulador de energia regenerativa em suspensões veiculares",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
async def root():
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.post("/calculate", response_model=RouteResponse)
async def calculate_energy(request: RouteRequest):
    try:
        origin_lat, origin_lon = await geocode_address(request.origin)
        dest_lat, dest_lon = await geocode_address(request.destination)

        route = await get_route(origin_lat, origin_lon, dest_lat, dest_lon)

        coordinates = route["geometry"]["coordinates"]
        pavement_data = await get_pavement_data(coordinates)

        segments = []

        for data in pavement_data:
            segment = Segment(
                distance=data["distance"],
                duration=data["distance"] / 10,
                surface=data["surface"],
                iri=data["iri"],
                coordinates=[data["start"], data["end"]]
            )
            segments.append(segment)

        total_distance_m = route["distance"]
        total_duration_s = route["duration"]

        average_speed_ms = (
            total_distance_m / total_duration_s
            if total_duration_s > 0
            else 10
        )

        segments_dict = [
            {
                "iri": s.iri,
                "distance": s.distance,
                "surface": s.surface
            }
            for s in segments
        ]

        result = calculate_energy_ferreira_2013(
            segments_dict,
            request.vehicle_type,
            average_speed_ms
        )

        energy_result = EnergyResult(**result)
        energy_average = result["energy_wh"]
        comparisons = generate_comparisons(energy_average)

        return RouteResponse(
            total_distance_km=round(total_distance_m / 1000, 2),
            total_duration_min=round(total_duration_s / 60, 1),
            segments=segments,

            energy_method_1=energy_result,
            energy_method_2=energy_result,
            energy_method_3=energy_result,

            energy_average=round(energy_average, 3),
            energy_min=round(energy_average, 3),
            energy_max=round(energy_average, 3),
            comparisons=comparisons
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )


@app.get("/vehicle-types")
async def get_vehicle_types():
    return {
        "types": [
            {"id": "car", "name": "Carro popular", "description": "Veículo de passeio comum"},
            {"id": "suv", "name": "SUV", "description": "Utilitário esportivo"},
            {"id": "bus", "name": "Ônibus", "description": "Ônibus urbano"},
            {"id": "truck", "name": "Caminhão", "description": "Caminhão médio"}
        ]
    }