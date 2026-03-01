from flask import Blueprint, request, jsonify
from math import radians, cos, sin, sqrt, atan2

gps_bp = Blueprint('gps', __name__)

# Example campus coordinates
CAMPUS_LAT = 18.03
CAMPUS_LONG = 74.03
GEO_RADIUS = 0.1  # km

def distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

@gps_bp.route('/verify', methods=['POST'])
def verify_gps():
    data = request.json
    lat = float(data.get('lat'))
    lon = float(data.get('lon'))
    d = distance(lat, lon, CAMPUS_LAT, CAMPUS_LONG)
    return jsonify({'within_geofence': d <= GEO_RADIUS})
