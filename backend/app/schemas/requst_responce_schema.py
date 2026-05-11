from datetime import UTC, datetime

from pydantic import BaseModel, Field

from backend.app.schemas.star_constellation_schema import ConstellationSchema, StarSchema


class SkyRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SkyResponse(BaseModel):
    astronomy_time: float
    stars: list[StarSchema]
    constellations: list[ConstellationSchema]
