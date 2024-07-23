import re


class PathStyler:
    def __init__(self, tags, styleRule):
        self.__tags = tags
        self._styleRule = styleRule

    def _get_matching_tags(self):
        matching_tags = {}

        key_regex = re.compile(self._styleRule["key"])
        matching_keys = list(filter(key_regex.match, self.__tags))

        for matching_key in matching_keys:
            matching_tags[matching_key] = self.__tags[matching_key]

        return matching_tags

    def _get_matching_values(self):
        matching_tags = self._get_matching_tags()
        matching_values = {}

        for matching_tag in matching_tags.items():
            value_regex = re.compile(self._styleRule["value"])
            value_regex_match = value_regex.match(matching_tag[1])
            value_regex_matches = []

            if value_regex_match:
                value_regex_matches.extend((value_regex_match.group(),))
                matching_values[matching_tag[0]] = value_regex_matches
        
        return matching_values

    def get_ruleset(self, value):
        ruleset = ""

        if value is not None:
            for styleDeclaration in self._styleRule["style"]:
                ruleset += "{property}:{value};".format(
                    property=styleDeclaration["property"],
                    value=styleDeclaration["value"].format(value=value))

        return ruleset
