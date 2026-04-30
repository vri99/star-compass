from pydantic import BaseModel

class StarSchema(BaseModel):
    # 3D cords
    x: float
    y: float
    z: float
    # brightness
    mag: float
    # attributes
    name: str
    constellation_name: str

class ConstellationSchema(BaseModel):
    name: str
    stars: list[StarSchema]
    lines: list[tuple[str, str]]

