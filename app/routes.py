"""
Details :--

- **Imports**:
  - `Blueprint`, `request`, `jsonify` from `quart`
  - `ObjectId` from `bson.objectid`
  - `ValidationError` from `pydantic`
  - `GeoDataManager` from `app.models`
  - `PointDataSchema`, `PolygonDataSchema` from `app.schemas`

- **Routes**:
  - **`/adding_details` (POST)**: Creates a point with validation, checks for existing locations, and returns ID.
  - **`/adding_details/<id>` (GET)**: Retrieves a point by ID.
  - **`/adding_details/<id>` (PUT)**: Updates a point by ID with validation.
  - **`/adding_polygons_details` (POST)**: Creates a polygon with validation, checks for existing locations, and returns ID.
  - **`/adding_polygons_details/<id>` (PUT)**: Updates a polygon by ID with validation.
  - **`/adding_polygons_details/<id>` (GET)**: Retrieves a polygon by ID and includes density.

  -- details referance ChatGpt

"""

from quart import Blueprint, request, jsonify
from bson.objectid import ObjectId
from pydantic import ValidationError
from app.models import GeoDataManager
from app.schemas import PointDataSchema, PolygonDataSchema
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import asyncio

api_bp = Blueprint('api', __name__)

mongo_uri = 'mongodb://localhost:27017'
db_name = "spatialdb"

loop = asyncio.get_event_loop()

db = GeoDataManager(mongo_uri,db_name)


# routes to retrive data from map using geo py for longitude and latitude :

@api_bp.route('/locationdetails', methods=['GET'])
async def get_location_details():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    # Check if latitude and longitude are provided
    if not latitude or not longitude:
        return jsonify({"error": "Missing latitude or longitude"}), 400

    # Validate latitude and longitude format
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({"error": "Invalid latitude or longitude format"}), 400

    # Validate latitude and longitude ranges
    if not (-90 <= latitude <= 90):
        return jsonify({"error": "Latitude must be between -90 and 90"}), 400

    if not (-180 <= longitude <= 180):
        return jsonify({"error": "Longitude must be between -180 and 180"}), 400

    # Asynchronous handling of geolocation
    geolocator = Nominatim(user_agent="location_api")

    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
        #await loop.run_in_executor(None, geolocator.reverse, (latitude, longitude), True)
    except GeopyError as e:
        return jsonify({"error": "Geolocation service error", "details": str(e)}), 500

    if location is None:
        return jsonify({"error": "Location not found"}), 404
    
    # Ensure unique location constraint if needed
    existing_point = await db.get_point_by_location(location.address)  
    if existing_point:
        return jsonify({'error': f"Point with location '{location.address}' already exists"}), 409
    point_id = await db.insert_point(location.address,latitude, longitude, location.raw) 

    return jsonify({
        'id': str(point_id),
        "location": location.address,
        "latitude": latitude,
        "longitude": longitude,
        "details": location.raw
    }), 200

# routes to retrive data from map using geo py based on locations :
@api_bp.route('/getBasedOnlocation', methods=['GET'])
async def get_details_based_on_location():
    location_name = request.args.get('location')

    # Check if location name is provided
    if not location_name:
        return jsonify({"error": "Missing location name"}), 400

    geolocator = Nominatim(user_agent="location_api")

    try:
        location = geolocator.geocode(location_name, exactly_one=True)
    except GeopyError as e:
        return jsonify({"error": "Geolocation service error", "details": str(e)}), 500

    if location is None:
        return jsonify({"error": "Location not found"}), 404

    # Ensure unique location constraint if needed
    existing_point = await db.get_point_by_location(location.address)
    if existing_point:
        return jsonify({'error': f"Point with location '{location.address}' already exists"}), 409
    
    point_id = await db.insert_point(location.address, location.latitude, location.longitude, location.raw)

    return jsonify({
        'id': str(point_id),
        "location": location.address,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "details": location.raw
    }), 200


# adding some details for specific adding_details

@api_bp.route('/adding_details', methods=['POST'])
async def create_point():
    try:
        data = await request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Check for required attributes
        required_fields = ['location', 'longitude', 'latitude', 'details']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Validate input data using Pydantic schema
        data = PointDataSchema(**data)
        
        # Ensure unique location constraint if needed
        existing_point = await db.get_point_by_location(data.location)  
        if existing_point:
            return jsonify({'error': f"Point with location '{data.location}' already exists"}), 409

        point_id = await db.insert_point(data.location, data.longitude, data.latitude)  
        return jsonify({'id': str(point_id)}), 201

    except ValidationError as e:
        return jsonify({'validation_errors': e.errors()}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/adding_details/<id>', methods=['GET'])
async def get_point(id):
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'Invalid ID format'}), 400

        point = await db.get_point_by_id(ObjectId(id))  
        if not point:
            return jsonify({'error': 'Point not found'}), 404
        
        return jsonify({'id': str(point['_id']), 'location': point['location']}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/adding_details/<id>', methods=['PUT'])
async def update_point_route(id):
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'Invalid ID format'}), 400

        # Check for required attributes
        data = await request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['location', 'longitude', 'latitude']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f"Missing fields: {', '.join(missing_fields)}"}), 400
        
        # Validate input data using Pydantic schema
        data = PointDataSchema(**data)
        
        # Check if point exists
        point = await db.get_point_by_id(ObjectId(id))  
        if not point:
            return jsonify({'error': 'Point not found'}), 404
        
        # Update point
        result = await db.update_point(ObjectId(id), data.location, data.longitude, data.latitude)  
        return jsonify({'message': 'Point updated'}), 200 if result.matched_count > 0 else 404

    except ValidationError as e:
        return jsonify({'validation_errors': e.errors()}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Polygons routes

@api_bp.route('/adding_polygons_details', methods=['POST'])
async def create_polygon():
    try:
        data = await request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Check for required attributes
        required_fields = ['location', 'coordinates', 'density', 'details']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Validate input data using Pydantic schema
        data = PolygonDataSchema(**data)
        
        # Ensure unique location constraint if needed
        existing_polygon = await db.get_polygon_by_location(data.location)  
        if existing_polygon:
            return jsonify({'error': f"Polygon with location '{data.location}' already exists"}), 409

        # Insert polygon with density
        polygon_id = await db.insert_polygon(data.location, data.coordinates, data.density)  
        return jsonify({'id': str(polygon_id)}), 201

    except ValidationError as e:
        return jsonify({'validation_errors': e.errors()}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/adding_polygons_details/<id>', methods=['PUT'])
async def update_polygon_route(id):
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'Invalid ID format'}), 400

        # Check for required attributes
        data = await request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['location', 'coordinates', 'density']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f"Missing fields: {', '.join(missing_fields)}"}), 400
        
        # Validate input data using Pydantic schema
        data = PolygonDataSchema(**data)
        
        # Check if polygon exists
        polygon = await db.get_polygon_by_id(ObjectId(id))  
        if not polygon:
            return jsonify({'error': 'Polygon not found'}), 404
        
        # Update polygon with density
        result = await db.update_polygon(ObjectId(id), data.location, data.coordinates, data.density)  
        return jsonify({'message': 'Polygon updated'}), 200 if result.matched_count > 0 else 404

    except ValidationError as e:
        return jsonify({'validation_errors': e.errors()}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/adding_polygons_details/<id>', methods=['GET'])
async def get_polygon(id):
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'Invalid ID format'}), 400

        polygon = await db.get_polygon_by_id(ObjectId(id))  
        if not polygon:
            return jsonify({'error': 'Polygon not found'}), 404

        return jsonify({
            'id': str(polygon['_id']),
            'location': polygon['location'],
            'coordinates': polygon['coordinates'],
            'density': polygon['density'], 
            'details': polygon['details']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
