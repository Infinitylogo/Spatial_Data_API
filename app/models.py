from .db import mongo

def insert_point(name, longitude, latitude):
    point = {
        "name": name,
        "location": {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }
    }
    return mongo.db.points.insert_one(point).inserted_id

def get_point_by_id(point_id):
    return mongo.db.points.find_one({"_id": point_id})

def update_point(point_id, name, longitude, latitude):
    return mongo.db.points.update_one(
        {"_id": point_id},
        {"$set": {
            "name": name,
            "location": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }
        }}
    )

def insert_polygon(name, coordinates):
    polygon = {
        "name": name,
        "location": {
            "type": "Polygon",
            "coordinates": coordinates
        }
    }
    return mongo.db.polygons.insert_one(polygon).inserted_id

def get_polygon_by_id(polygon_id):
    return mongo.db.polygons.find_one({"_id": polygon_id})

def update_polygon(polygon_id, name, coordinates):
    return mongo.db.polygons.update_one(
        {"_id": polygon_id},
        {"$set": {
            "name": name,
            "location": {
                "type": "Polygon",
                "coordinates": coordinates
            }
        }}
    )
