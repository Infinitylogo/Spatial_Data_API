from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from pydantic import ValidationError
from app.models import insert_point, get_point_by_id, update_point, insert_polygon, get_polygon_by_id, update_polygon
from app.schemas import PointDataSchema, PolygonDataSchema

api_bp = Blueprint('api', __name__)


@api_bp.route('/points', methods=['POST'])
def create_point():
    try:
        data = request.get_json() 
        data = PointDataSchema(**data)
        point_id = insert_point(data.name, data.longitude, data.latitude)
        return jsonify({'id': str(point_id)}), 201
    except ValidationError as e:
        return jsonify(e.errors()), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Handle other exceptions

@api_bp.route('/points/<id>', methods=['GET'])
def get_point(id):
    point = get_point_by_id(ObjectId(id))
    if not point:
        return jsonify({'error': 'Point not found'}), 404
    return jsonify({'id': str(point['_id']), 'name': point['name'], 'location': point['location']}), 200

@api_bp.route('/points/<id>', methods=['PUT'])
def update_point_route(id):
    try:
        data = PointDataSchema(**request.json)
        result = update_point(ObjectId(id), data.name, data.longitude, data.latitude)
        if result.matched_count == 0:
            return jsonify({'error': 'Point not found'}), 404
        return jsonify({'message': 'Point updated'}), 200
    except ValidationError as e:
        return jsonify(e.errors()), 400
    

## Polygons routes >>>>>>>>>>>>>>

@api_bp.route('/polygons', methods=['POST'])
def create_polygon():
    try:
        data = PolygonDataSchema(**request.json)
        polygon_id = insert_polygon(data.name, data.coordinates)
        return jsonify({'id': str(polygon_id)}), 201
    except ValidationError as e:
        return jsonify(e.errors()), 400

@api_bp.route('/polygons/<id>', methods=['GET'])
def get_polygon(id):
    polygon = get_polygon_by_id(ObjectId(id))
    if not polygon:
        return jsonify({'error': 'Polygon not found'}), 404
    return jsonify({'id': str(polygon['_id']), 'name': polygon['name'], 'location': polygon['location']}), 200

@api_bp.route('/polygons/<id>', methods=['PUT'])
def update_polygon_route(id):
    try:
        data = PolygonDataSchema(**request.json)
        result = update_polygon(ObjectId(id), data.name, data.coordinates)
        if result.matched_count == 0:
            return jsonify({'error': 'Polygon not found'}), 404
        return jsonify({'message': 'Polygon updated'}), 200
    except ValidationError as e:
        return jsonify(e.errors()), 400
