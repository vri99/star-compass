from pydantic import BaseModel


class StarSchema(BaseModel):
    # ICRS coordinates
    ra: float
    dec: float

    # brightness
    mag: float
    # attributes
    name: str
    constellation_name: str


class ConstellationSchema(BaseModel):
    name: str
    stars: list[StarSchema]
    lines: list[list[str]]
