from pydantic import BaseModel


class StarSchema(BaseModel):
    # id
    hip: str
    # ICRS coordinates
    ra: float
    dec: float

    alt: float
    az: float

    # brightness
    mag: float
    # attributes
    name: str
    constellation_name: str


class ConstellationSchema(BaseModel):
    id: str
    full_name: str
    lines: list[list[str]]
