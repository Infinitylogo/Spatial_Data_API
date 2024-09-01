"""
Details :--

- **Imports**:
  - `Blueprint`, `request`, `jsonify` from `quart`
  - `ObjectId` from `bson.objectid`
  - `ValidationError` from `pydantic`
  - `GeoDataManager` from `app.models`
  - `PointDataSchema`, `PolygonDataSchema` from `app.schemas`

- **Routes**:
  - **`/points` (POST)**: Creates a point with validation, checks for existing locations, and returns ID.
  - **`/points/<id>` (GET)**: Retrieves a point by ID.
  - **`/points/<id>` (PUT)**: Updates a point by ID with validation.
  - **`/polygons` (POST)**: Creates a polygon with validation, checks for existing locations, and returns ID.
  - **`/polygons/<id>` (PUT)**: Updates a polygon by ID with validation.
  - **`/polygons/<id>` (GET)**: Retrieves a polygon by ID and includes density.

"""

from quart import Blueprint, request, jsonify
from bson.objectid import ObjectId
from pydantic import ValidationError
from app.models import GeoDataManager
from app.schemas import PointDataSchema, PolygonDataSchema

api_bp = Blueprint('api', __name__)

mongo_uri = 'mongodb://localhost:27017'
db_name = "spatialdb"

db = GeoDataManager(mongo_uri,db_name)

@api_bp.route('/points', methods=['POST'])
async def create_point():
    try:
        data = await request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Check for required attributes
        required_fields = ['location', 'longitude', 'latitude']
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

@api_bp.route('/points/<id>', methods=['GET'])
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

@api_bp.route('/points/<id>', methods=['PUT'])
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

@api_bp.route('/polygons', methods=['POST'])
async def create_polygon():
    try:
        data = await request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Check for required attributes
        required_fields = ['location', 'coordinates', 'density']
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

@api_bp.route('/polygons/<id>', methods=['PUT'])
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

@api_bp.route('/polygons/<id>', methods=['GET'])
async def get_polygon(id):
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'Invalid ID format'}), 400

        polygon = await db.get_polygon_by_id(ObjectId(id))  
        if not polygon:
            return jsonify({'error': 'Polygon not found'}), 404

        # Include density in the response
        return jsonify({
            'id': str(polygon['_id']),
            'location': polygon['location'],
            'coordinates': polygon['coordinates'],
            'density': polygon['density']  # Include density
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
