import hashlib
import json
import importlib
import os
import re
import urllib.error
import urllib.parse
import urllib.request

import svg

import mercator
import svg_path_d


class Request:
    def __init__(self, overpassQuery, path, update, cache):
        self.__overpassQuery = overpassQuery
        self.__path = path
        if update:
            try:
                self.data = self.__fetch_data()
                if cache:
                    self.__cache_data()
            except urllib.error.URLError:
                self.data = self.__read_cached_data()
        else:
            try:
                self.data = self.__read_cached_data()
            except FileNotFoundError:
                self.data = self.__fetch_data()
                if cache:
                    self.__cache_data()

    def __fetch_data(self):
        url_query = urllib.parse.urlencode({
            "data": self.__overpassQuery
        })
        request = urllib.request.Request(
            f"https://overpass-api.de/api/interpreter?{url_query}")
        with urllib.request.urlopen(request) as response:
            return response.read()

    def __read_cached_data(self):
        with open("/".join(self.__path), "rb") as cache_file:
            return cache_file.read()

    def __cache_data(self):
        #   Create cache directories if they don't exist
        for i in range(1, len(self.__path)):
            if not os.path.isdir("/".join(self.__path[0:i])):
                os.mkdir("/".join(self.__path[0:i]))

        with open("/".join(self.__path), "wb") as data_file:
            data_file.write(self.data)


class JSONElements:
    def __init__(self, group, update, rules, sort, **kwargs):
        self.__group = group
        self.__update = update
        self.__rules = rules
        self.__kwargs = kwargs
        self.elements = self.fetch_elements()
        if sort:
            self.sort_elements()

    def fetch_elements(self):
        string_to_hash = ";".join(
            self.__rules["city_query_parameters"].values())
        hash = hashlib.sha224(string_to_hash.encode("utf-8")).hexdigest()
        cache_path = ("cache", hash, f"{self.__group}.json")

        #   Get OSM data with Overpass API
        query_path = ("queries", f"{self.__group}.txt")
        with open("/".join(query_path), "r") as query_file:
            query = query_file.read().format(**self.__kwargs)
            request = Request(
                query, cache_path, self.__update, cache=True)

        data = json.loads(request.data)

        return data["elements"]

    def sort_elements(self):
        elements_values = []
        for element in self.elements:
            values = []
            for rule in self.__rules["style_rules"]["dynamic"]:
                if rule["group"] == self.__group:
                    path_styler = importlib.import_module(
                        rule["module"])
                    value = path_styler.PathStyler(
                        element["tags"], rule).get_value()
                else:
                    value = None
                values.append(value if value is not None else 0)
            elements_values.append(values)

        for i in range(len(self.__rules["style_rules"]["dynamic"]), 0, -1):
            self.elements = [element for element, elementValues in sorted(
                zip(self.elements, elements_values), key=lambda pair: pair[1][i-1])]


class SVGElements:
    def __init__(self, group, elements, rules):
        self.__group = group
        self.__elements = elements
        self.__rules = rules

    def _get_element_classes(self, tags):
        class_names = [self.__group]

        for rule in self.__rules["style_rules"]["static"]:
            key_regex = re.compile(rule["key"])
            matching_keys = filter(key_regex.match, tags.keys())
            for matching_key in matching_keys:
                value_regex = re.compile(rule["value"])
                if value_regex.match(tags[matching_key]):
                    class_names.append(rule["class"])
                    break

        return class_names

    def _get_element_style(self, tags):
        style = ""

        for rule in self.__rules["style_rules"]["dynamic"]:
            if rule["group"] == self.__group:
                path_styler = importlib.import_module(
                    rule["module"])
                style += path_styler.PathStyler(tags, rule).get_ruleset()

        return style

    def get_elements(self):
        svg_elements = []
        for overpass_element in self.__elements:
            class_ = self._get_element_classes(overpass_element["tags"])
            style = self._get_element_style(overpass_element["tags"])
            match overpass_element["type"]:
                case "node":
                    svg_element = svg.Circle(
                        cx=mercator.Mercator.longitude(overpass_element["lon"]),
                        cy=mercator.Mercator.latitude(overpass_element["lat"]),
                        class_=class_,
                        style=style
                    )
                case _:
                    svg_element = svg.Path(
                        d=svg_path_d.PathD(overpass_element).d,
                        class_=class_,
                        style=style
                    )
                    if overpass_element["type"] == "way" and overpass_element["geometry"][0] == overpass_element["geometry"][-1]:
                        svg_element.class_.append("area")
            svg_elements.append(svg_element)

        return svg_elements
