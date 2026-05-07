from datetime import UTC, datetime, timezone

from backend.app.schemas.star_constellation_schema import ConstellationSchema
from pydantic import BaseModel, Field


class SkyRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SkyResponse(BaseModel):
    constellations: list[ConstellationSchema]
    astronomy_time: float
