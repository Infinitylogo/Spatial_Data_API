from pydantic import BaseModel, Field, conlist
from typing import List, Tuple

class PointDataSchema(BaseModel):
    name: str
    longitude: float
    latitude: float


class PolygonDataSchema(BaseModel):
    name: str
    coordinates: List[Tuple[float, float]]