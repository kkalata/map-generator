import argparse
import concurrent.futures
import itertools
import json
import logging

import svg

import bbox
import overpass


#   Constants
SETTINGS_PATH = "settings.json"


def load_file(path):
    with open(path, "r") as file:
        return file.read()


def load_json_file(path):
    with open(path, "rb") as file:
        return json.load(file)


def prepare_svg_elements(group, rules, update, kwargs):
    try:
        logging.info(f"Started getting elements of {group}")
        elements = overpass.JSONElements(
            group, update, rules, sort=False if group != "building" else False, **kwargs).elements
        logging.info(f"Got elements of {group}")
    except:
        logging.info(
            f"An error occured while getting elements of {group}, skipping...")
        return []
    
    try:
        logging.info(f"Started preparing paths of {group}")
        svg_elements = overpass.SVGElements(
            group, elements, rules).get_elements()
        logging.info(f"Prepared paths of {group}")

        return svg_elements
    except:
        import traceback
        traceback.print_exc()
        logging.info(
            f"An error occured while preparing elements of {group}, skipping...")
        return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update",
        help="update cache",
        action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        style="{",
        format="[{asctime}] {message}",
        level=logging.INFO)
    logging.info("Started generating")

    settings = load_json_file(SETTINGS_PATH)
    logging.info("Loaded settings")

    rules = load_json_file(settings["rules_path"])
    logging.info("Loaded rules")

    #   Create basic SVG structure
    canvas = svg.SVG(elements=[
        svg.Desc(text=load_file("desc.txt")),
        svg.Style(text=load_file(rules["css_path"])),
    ])

    try:
        overpass_bbox = overpass.JSONElements(
            "city",
            args.update,
            rules,
            sort=False,
            **rules["city_query_parameters"]).elements

        city_bbox = None

        for element in overpass_bbox:
            if city_bbox is None:
                city_bbox = bbox.BBox(bounds=element["bounds"])
            else:
                city_bbox.expand(element["bounds"])
        canvas.viewBox = svg.ViewBoxSpec(
            **city_bbox.get_viewbox_format(convert_to_mercator=True))

        kwargs_groups = []
        for group in rules["groups"]:
            if group == "city":
                kwargs_groups.append(rules["city_query_parameters"])
            else:
                kwargs_groups.append({"bbox": city_bbox.get_overpass_format()})
        with concurrent.futures.ThreadPoolExecutor(len(rules["groups"])) as executor:
            for group, elements in zip(
                rules["groups"],
                executor.map(
                    prepare_svg_elements,
                    rules["groups"],
                    itertools.repeat(rules),
                    itertools.repeat(args.update),
                    kwargs_groups
                )
            ):
                canvas.elements.extend(elements)
                logging.info(f"Added elements of {group} to SVG structure")

        canvas.elements.append(svg.Text(x=city_bbox.get_east(convert_to_mercator=True) - 8,
                                        y=city_bbox.get_south(convert_to_mercator=True) - 8,
                                        style=f"font-size:{(city_bbox.get_height(convert_to_mercator=True)) * 0.011}px;",
                                        text=load_file("desc.txt")))

        logging.info("Started writing map to SVG file")
        with open("map.svg", "w") as svg_file:
            svg_file.write(canvas.as_str())
        logging.info("Wrote map to SVG file")

        logging.info("Finished generating")
    except:
        logging.info(
            f"An error occured while getting elements of bbox, stopping...")
