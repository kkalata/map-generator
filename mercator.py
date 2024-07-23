import math

class Mercator:
    @staticmethod
    def latitude(latitude, scale=1e6, precision=10):
        latitude = scale * \
            math.log(math.tan(math.pi / 4 + (-latitude * math.pi / 180) / 2))
        return round(latitude, precision)

    @staticmethod
    def longitude(longitude, scale=1e6, precision=10):
        longitude = scale * longitude * math.pi / 180
        return round(longitude, precision)

    @staticmethod
    def node(node):
        return {
            "x": Mercator.longitude(node["lon"]),
            "y": Mercator.latitude(node["lat"])
        }
