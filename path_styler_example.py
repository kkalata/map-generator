import path_styler


class PathStyler(path_styler.PathStyler):
    def get_value(self):
        value = None
        matching_values = self._get_matching_values()

        for matching_tag_values in matching_values.items():
            for matching_tag_value in matching_tag_values[1]:
                if value is not None:
                    value = max(int(matching_tag_value.split()[0]), value)
                else:
                    value = int(matching_tag_value.split()[0])
                if "mph" in matching_tag_value:
                    value *= 1.609

        return value

    def get_ruleset(self):
        try:
            value = -2 * self.get_value() + 240
            ruleset = super().get_ruleset(value)
        except:
            ruleset = ""
        
        return ruleset    
