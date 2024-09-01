from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


"""
- **Imports**:
  - `AsyncIOMotorClient` from `motor.motor_asyncio`
  - `ObjectId` from `bson`

- **Class: `GeoDataManager`**:
  - **Constructor**:
    - Initializes `AsyncIOMotorClient` with `db_uri`
    - Sets the database to `db_name`

  - **Methods**:
    - `insert_point(name, longitude, latitude)`: Inserts a point into `points` collection, returns ID.
    - `get_point_by_id(point_id)`: Retrieves a point by ID, returns `None` if invalid.
    - `get_point_by_location(location)`: Retrieves a point by name.
    - `update_point(point_id, name, longitude, latitude)`: Updates a point by ID, returns result or `None`.
    - `insert_polygon(location, coordinates, density)`: Inserts a polygon into `polygons`, returns ID.
    - `get_polygon_by_id(polygon_id)`: Retrieves a polygon by ID, returns `None` if invalid.
    - `update_polygon(polygon_id, location, coordinates, density)`: Updates a polygon by ID, returns result or `None`.
    - `get_polygon_by_location(location)`: Retrieves a polygon by location.
"""


class GeoDataManager:
    def __init__(self, db_uri, db_name):
        self.client = AsyncIOMotorClient(db_uri)
        self.db = self.client[db_name]

    async def insert_point(self, name, longitude, latitude):
        point = {
            "name": name,
            "location": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }
        }
        result = await self.db.points.insert_one(point)
        return result.inserted_id

    async def get_point_by_id(self, point_id):
        if not ObjectId.is_valid(point_id):
            return None
        return await self.db.points.find_one({"_id": ObjectId(point_id)})

    async def get_point_by_location(self, location):
        return await self.db.points.find_one({"name": location})

    async def update_point(self, point_id, name, longitude, latitude):
        if not ObjectId.is_valid(point_id):
            return None
        result = await self.db.points.update_one(
            {"_id": ObjectId(point_id)},
            {"$set": {
                "name": name,
                "location": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                }
            }}
        )
        return result

    async def insert_polygon(self, location, coordinates, density):
        result = await self.db.polygons.insert_one({
            'location': location,
            'coordinates': coordinates,
            'density': density
        })
        return result.inserted_id

    async def get_polygon_by_id(self, polygon_id):
        if not ObjectId.is_valid(polygon_id):
            return None
        return await self.db.polygons.find_one({"_id": ObjectId(polygon_id)})

    async def update_polygon(self, polygon_id, location, coordinates, density):
        if not ObjectId.is_valid(polygon_id):
            return None
        result = await self.db.polygons.update_one(
            {'_id': ObjectId(polygon_id)},
            {'$set': {
                'location': location,
                'coordinates': coordinates,
                'density': density
            }}
        )
        return result
    
    async def get_polygon_by_location(self, location):
        return await self.db.polygons.find_one({"location":location})

