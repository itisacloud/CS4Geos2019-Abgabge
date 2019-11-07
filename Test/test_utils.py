import sys
import os
import unittest
import numpy as np
from src.utils_geojson import *
from src.utils import *
from shapely.geometry import Polygon


class test_utils(unittest.TestCase()):
    def test_load_geojson_to_dict(self):
        path = "test\\geojson_test.geojson"
        expected_type = "Polygon"
        expected_coordinates = [[3,4],[4,4],[4,3],[1,0],[0,0],[0,1]]
        result = load_geojson_features_to_dict(path)
        assert result[0]["geometry"]["type"]==expected_type
        assert result[0]["geometry"]["coordinates"]==expected_coordinates


    def test_get_bbox(self):
        path = "test\\geojson_test.geojson"
        features = load_geojson_features_to_dict(path)
        expected = [0,0,4,4]
        result = get_bbox(features)
        assert result == expected

    def test_transform_polygon(self):
        polygon = transform_geometry(Polygon([[3,4],[4,3],[4,3]]),'epsg:32632')
        print(polygon)
        assert isinstance(polygon,Polygon)


    def test_get_geom_list(self):
        path = "test\\geojson_test.geojson"
        features = load_geojson_features_to_dict(path)
        result = get_geom_list(features,0)
        assert isinstance(result,list)



if __name__ == "__main__"
    unittest.main()