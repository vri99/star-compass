from backend.app.models.interfaces import StarInterface

class StarModel(StarInterface):
    _ra: float
    _dec: float

    _alt: float
    _az: float

    _mag: float

    _name: str