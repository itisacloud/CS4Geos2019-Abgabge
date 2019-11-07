'''
# This Script calculates the NDVI for features in a GeoJSON,
# which it calculates based on data fetched via satsearch
# [landsat 8 or sentinel 2(sentinel is on amazon aws currently behind a paywall,
# so it might not work)
# inputs: a config .json example found on github, geojson
# requierments: rasterio, satsearch, shapely, numpy, matplotlib, pyproj, python 3+
# output: (optional) Plots per feature, (optional) a geojson with the new
# Author: Clemens Langer
'''

import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from satsearch import Search

from src.utils import download_band, get_url_pair, calculate_ndvi, create_mask, grab_values_by_mask, get_geom_list
from src.utils_geojson import load_geojson_features_to_dict, get_bbox
from src.utils_overpass import grab_osm_data


if __name__ == '__main__':
    try:
        CONFIG_FILE = sys.argv[1]
    except IndexError:
        print("This script requieres a config .json, please enter a valid path")
        sys.exit()
    try:
        with open(CONFIG_FILE) as cf:
            CONFIGS = json.load(cf)
        print("got the following configurations out of file {}".format(
            CONFIG_FILE.split('\\')[-1]))
        print(CONFIGS)
        JSON_PATH = CONFIGS["json_path"]
        BUFFER_DISTANCE = CONFIGS["buffer distance"]
        DATETIME_FRAME = CONFIGS["datetimeframe"]
        COLLECTION = CONFIGS["collection"]
        PROPERTY = CONFIGS["property"]
        SHOW_PLOTS = CONFIGS["show_plots"]
        GENERATE_GEOJSON = CONFIGS["generate_geojson"]
        OSM = CONFIGS["osm"]
        OUTPUT_PATH = CONFIGS["output_path"]
        if OSM:
            OSM_DATA = CONFIGS["osm_query"]
    except KeyError as error:
        print("Invalid Config file, propaly not all ")
        print(error)
        sys.exit()
    assert os.path.exists(JSON_PATH), "Json file does not exist"

    try:
        FEATURES = load_geojson_features_to_dict(JSON_PATH)
        if OSM:
            FEATURES = grab_osm_data(OSM_DATA, FEATURES)
        BBOX = get_bbox(FEATURES)
        GEOM_LIST = get_geom_list(FEATURES,BUFFER_DISTANCE)
        SEARCH = Search.search(
            bbox=BBOX,
            datetime=DATETIME_FRAME,
            collection=COLLECTION,
            property=PROPERTY)

        ITEMS = SEARCH.items()
        print("Found {} tiles matching".format(SEARCH.found()))
        DATE_LIST = []
        NDVI_LIST = []

        for i in range(len(FEATURES)):
            NDVI_LIST.append([])
            DATE_LIST.append([])

        for item_counter ,item in enumerate(ITEMS):
            print("Processing Tile {} of {}".format(item_counter+1, len(ITEMS)))
            URL_PAIR = get_url_pair(item, COLLECTION)
            RED_BAND = download_band(URL_PAIR[0], BBOX)
            NIR_BAND = download_band(URL_PAIR[1], BBOX)
            NDVI_BAND = calculate_ndvi(RED_BAND[0], NIR_BAND[0])
            MASK = create_mask(GEOM_LIST, *RED_BAND[0].shape, *RED_BAND[1::])
            NDVI_VALUES = grab_values_by_mask(MASK, NDVI_BAND)
            for i, ndvi in enumerate(NDVI_VALUES):
                ndvi = [ndvi_value for ndvi_value in ndvi if -1 <= ndvi_value <= 1]
                ndvi_mean = np.mean(ndvi)
                if not np.isnan(ndvi_mean):
                    NDVI_LIST[i].append(ndvi_mean)
                    DATE_LIST[i].append(item.date)

        if SHOW_PLOTS:
            for i in range(len(NDVI_LIST)):

                plt.plot(DATE_LIST[i], NDVI_LIST[i])
                print(DATE_LIST[i])
                print(NDVI_LIST[i])
                try:
                    plt.title("NDVI Verlauf von {} bis {} für {}".format(DATE_LIST[i][0].strftime('%d\%m\%Y'),
                                                                     DATE_LIST[i][-1].strftime('%d\%m\%Y'),
                                                                     FEATURES[i]["properties"]["name"]))
                except KeyError:
                    print("Feature has no name, not title generated")
                plt.xlabel("Date")
                plt.ylabel("NDVI")
                plt.show()

        if GENERATE_GEOJSON:
            for i, feature in enumerate(FEATURES):
                feature["properties"]["ndvi"] = []
                for ndvi, date in zip(NDVI_LIST[i], DATE_LIST[i]):
                    feature["properties"]["ndvi"].append(
                        {'timestamp': date.strftime('%m%d%Y'), 'ndvi_value': ndvi})
            OUTPUT = {'type': 'FeatureCollection', 'features': FEATURES}

            OUTPUT_FILE = os.path.join(OUTPUT_PATH, CONFIG_FILE.split('\\')[-1].split('.')[0] + '.geojson')
            print(OUTPUT_FILE)
            with open(OUTPUT_FILE, '+w') as outfile:
                json.dump(OUTPUT, outfile)
    except AssertionError as error:
        print(error)
        print("exiting")
        sys.exit()
