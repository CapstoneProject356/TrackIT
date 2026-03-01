def verify_gps(lat, long):
    CLASS_LAT = 18.5204
    CLASS_LNG = 73.8567
    radius = 0.0005

    return abs(lat - CLASS_LAT) < radius and abs(long - CLASS_LNG) < radius
