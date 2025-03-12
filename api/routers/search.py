from fastapi import APIRouter
from services.network_fetcher import NetworkFetcher

router = APIRouter()

@router.get("/")
async def root():
    return {"Hello": "World"}

@router.get("/search/")
async def search(q: str):
    return NetworkFetcher(q).get_network_coverage()

@router.get("/search_under_km/")
async def search(q: str):
    """Endpoint used for developing purposes"""
    return NetworkFetcher(q).get_points_under_km()
