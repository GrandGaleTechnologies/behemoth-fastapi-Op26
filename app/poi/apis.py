from fastapi import APIRouter
from app.poi.routes.offense import router as poi_offense_router

router = APIRouter()

# Include routers
router.include_router(poi_offense_router, prefix="/offense", tags=["Offense APIs"])
