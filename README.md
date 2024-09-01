# Spatial_Data_API
API that help plot spatial Data on Maps

# Structure :-->>
<!-- 
SPATIAL_DATA_API/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── db.py
│   └── schemas.py
├── config.py
├── main.py
├── requirements.txt
└── README.md
-->

Simple dashboard-- ask for coordinates and show the diagram

create run.sh 
project is to store polygon, points along with data values in db
or check for some of the points based on db

for all the record in db, it should create show all points on dashboard  -- it is for location one 
for density one it should ask for options based on location we have in db -- it is for density one 


for points :--
curl -X POST http://localhost:5000/api/points -H "Content-Type: application/json" -d "{\"name\": \"Point A\", \"longitude\": 12.34, \"latitude\": 56.78}"


curl -X GET http://127.0.0.1:5000/api/points/66d46cd31c05f15572768245


# curls.txt

# 1. Update a Point (PUT /points/<id>)
# Replace <id> with the actual ObjectId of the point you want to update.
curl -X PUT http://127.0.0.1:5000/api/points/<id> \
-H "Content-Type: application/json" \
-d '{
  "name": "Updated Point Name",
  "longitude": 77.5946,
  "latitude": 12.9716
}'

# 2. Create a Polygon (POST /polygons)
# This command creates a new polygon with the provided name and coordinates.
curl -X POST http://127.0.0.1:5000/api/polygons \
-H "Content-Type: application/json" \
-d '{
  "name": "Polygon Name",
  "coordinates": [
    [77.5946, 12.9716],
    [77.5946, 12.9718],
    [77.5948, 12.9718],
    [77.5948, 12.9716],
    [77.5946, 12.9716]
  ]
}'

# 3. Get a Polygon by ID (GET /polygons/<id>)
# Replace <id> with the actual ObjectId of the polygon you want to retrieve.
curl -X GET http://127.0.0.1:5000/api/polygons/<id>

# 4. Update a Polygon (PUT /polygons/<id>)
# Replace <id> with the actual ObjectId of the polygon you want to update.
curl -X PUT http://127.0.0.1:5000/api/polygons/<id> \
-H "Content-Type: application/json" \
-d '{
  "name": "Updated Polygon Name",
  "coordinates": [
    [77.5946, 12.9716],
    [77.5946, 12.9718],
    [77.5948, 12.9718],
    [77.5948, 12.9716],
    [77.5946, 12.9716]
  ]
}'

# 5. Get a Point by ID (GET /points/<id>)
# Replace <id> with the actual ObjectId of the point you want to retrieve.
curl -X GET http://127.0.0.1:5000/api/points/<id>
