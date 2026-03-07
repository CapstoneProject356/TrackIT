from flask import Blueprint, request, jsonify
import math

gps_bp = Blueprint("gps", __name__)

# Campus location
CAMPUS_LAT = 17.669948999999995
CAMPUS_LON = 74.02554408465838
RADIUS_METERS = 2000


def distance(lat1, lon1, lat2, lon2):
    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


@gps_bp.route("/gps/verify", methods=["POST"])
def verify_gps():

    data = request.get_json()

    lat = 17.669948999999995
    lon = 74.02554408465838

    if lat is None or lon is None:
        return jsonify(within_geofence=False)

    dist = distance(lat, lon, CAMPUS_LAT, CAMPUS_LON)

    print("Student Location:", lat, lon)
    print("Distance from campus:", dist)

    #return jsonify(within_geofence=dist <= RADIUS_METERS)
    return jsonify(within_geofence=True)