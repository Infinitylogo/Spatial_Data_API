from app.db import mongo

class GeoDataManager:

    def insert_point(self,name, longitude, latitude):
        point = {
            "name": name,
            "location": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }
        }
        return mongo.db.points.insert_one(point).inserted_id

    def get_point_by_id(self,point_id):
        return mongo.db.points.find_one({"_id": point_id})

    def update_point(self, point_id, location, longitude, latitude):
        return mongo.db.points.update_one(
            {"_id": point_id},
            {"$set": {
                "location": location,
                "location": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                }
            }}
        )

    def insert_polygon(self, location, coordinates, density):
        return mongo.db.polygons.insert_one({
            'location': location,
            'coordinates': coordinates,
            'density': density
        }).inserted_id


    def get_polygon_by_id(self,polygon_id):
        return mongo.db.polygons.find_one({"_id": polygon_id})

    def update_polygon(self,polygon_id, location, coordinates, density):
        return mongo.db.polygons.update_one(
            {'_id': polygon_id},
            {'$set': {
                'location': location,
                'coordinates': coordinates,
                'density': density
            }}
        )
