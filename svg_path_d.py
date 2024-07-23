import svg

import mercator


class PathD:
    def __init__(self, element):
        match element["type"]:
            case "node" | "way":
                self.d = WayD(element["geometry"]).d
            case "relation":
                self.d = MultipolygonD(element["members"]).d


class WayD:
    def __init__(self, geometry):
        self.d = []
        first = True

        for node in geometry:
            if first:
                self.d.append(svg.M(**mercator.Mercator.node(node)))
                first = False
            else:
                self.d.append(svg.L(**mercator.Mercator.node(node)))


class MultipolygonD:
    def __init__(self, members):
        self.d = []

        way = []
        edge_nodes = {
            "first": None,
            "last": None,
        }

        while len(members) > 0:
            for relation_member in members:
                if relation_member["role"] in ("outer", "inner"):
                    if relation_member["type"] == "way":
                        relation_member_geometry = relation_member["geometry"]

                        #   Check whether way has a common node with the previous one
                        if edge_nodes["last"] is not None:
                            if relation_member_geometry[-1] == edge_nodes["last"]:
                                relation_member_geometry.reverse()
                            elif relation_member_geometry[0] != edge_nodes["last"]:
                                continue

                        if edge_nodes["first"] is None:
                            edge_nodes["first"] = relation_member_geometry[0]
                        edge_nodes["last"] = relation_member_geometry[-1]

                        way.extend(relation_member_geometry)

                        if edge_nodes["first"] == edge_nodes["last"]:
                            self.d.extend(WayD(way).d)
                            self.d.append(svg.Z())
                            way = []
                            edge_nodes = {
                                "first": None,
                                "last": None,
                            }
                members.remove(relation_member)
