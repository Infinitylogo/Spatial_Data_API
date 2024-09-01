from pydantic import BaseModel, Field, conlist
from typing import List, Tuple

class PointDataSchema(BaseModel):
    location: str
    longitude: float
    latitude: float


class PolygonDataSchema(BaseModel):
    location: str
    coordinates: List[Tuple[float, float]]
    density: float  