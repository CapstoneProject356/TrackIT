import math

def verify_gps(lat, long):

    # Convert to float
    lat = float(lat)
    long = float(long)

    # Classroom coordinates
    CLASS_LAT = 17.66873259157174
    CLASS_LNG = 74.02942927116362

    # Radius of Earth in meters
    R = 6371000

    # Convert degrees to radians
    lat1 = math.radians(lat)
    lon1 = math.radians(long)
    lat2 = math.radians(CLASS_LAT)
    lon2 = math.radians(CLASS_LNG)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distance = R * c

    print("Student Location:", lat, long)
    print("Class Location:", CLASS_LAT, CLASS_LNG)
    print("Distance from classroom:", distance, "meters")

    # Allow attendance if within 150 meters
    return distance < 150