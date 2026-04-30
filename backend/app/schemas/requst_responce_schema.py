from pydantic import BaseModel, Field
from datetime import datetime

from backend.app.schemas.star_constellation_schema import ConstellationSchema

class SkyRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    observed_at: datetime = Field(default_factory=datetime.utcnow)

class SkyResponse(BaseModel):
    constellations: list[ConstellationSchema] = []
