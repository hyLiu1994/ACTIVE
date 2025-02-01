import math

def haversine(positionA, positionB):
    lat1, lon1, lat2, lon2 = map(math.radians, [positionA[0], positionA[1], positionB[0], positionB[1]])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    radius = 6371
    return c * radius