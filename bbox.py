import mercator


class BBox:
    __north: float
    __south: float
    __west: float
    __east: float

    def __init__(self,
                 bounds: dict[str, float] = None,
                 bbox: "BBox" = None) -> None:
        if bounds != None:
            self.__north = bounds["maxlat"]
            self.__south = bounds["minlat"]
            self.__west = bounds["minlon"]
            self.__east = bounds["maxlon"]
        elif bbox != None:
            self.__north = bbox.__north
            self.__south = bbox.__south
            self.__west = bbox.__west
            self.__east = bbox.__east

    def __get_latitude_coord(self, coord, convert_to_mercator=False):
        if not convert_to_mercator:
            return coord
        else:
            return mercator.Mercator.latitude(coord)

    def __get_longitude_coord(self, coord, convert_to_mercator=False):
        if not convert_to_mercator:
            return coord
        else:
            return mercator.Mercator.longitude(coord)

    def get_north(self, convert_to_mercator=False):
        return self.__get_latitude_coord(self.__north, convert_to_mercator)

    def get_south(self, convert_to_mercator=False):
        return self.__get_latitude_coord(self.__south, convert_to_mercator)

    def get_west(self, convert_to_mercator=False):
        return self.__get_longitude_coord(self.__west, convert_to_mercator)

    def get_east(self, convert_to_mercator=False):
        return self.__get_longitude_coord(self.__east, convert_to_mercator)

    def get_width(self, convert_to_mercator=False) -> float:
        return self.get_east(convert_to_mercator) \
            - self.get_west(convert_to_mercator)

    def get_height(self, convert_to_mercator=False) -> float:
        return self.get_south(convert_to_mercator) \
            - self.get_north(convert_to_mercator)

    def get_overpass_format(self, convert_to_mercator=False) -> str:
        return "{south},{west},{north},{east}".format(
            north=self.get_north(convert_to_mercator),
            south=self.get_south(convert_to_mercator),
            west=self.get_west(convert_to_mercator),
            east=self.get_east(convert_to_mercator),
        )

    def get_viewbox_format(self, convert_to_mercator=False) -> dict[str, float]:
        return {
            "min_x": self.get_west(convert_to_mercator),
            "min_y": self.get_north(convert_to_mercator),
            "width": self.get_width(convert_to_mercator),
            "height": self.get_height(convert_to_mercator)
        }

    def expand(self, bounds: dict[str, float]) -> None:
        self.__north = max(self.__north, bounds["maxlat"])
        self.__south = min(self.__south, bounds["minlat"])
        self.__west = min(self.__west, bounds["minlon"])
        self.__east = max(self.__west, bounds["maxlon"])
