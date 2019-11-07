"""
Utils for handeling geojsons
"""
import os
import json

def load_geojson_features_to_dict(path):
    ''' takes the path to a geojson and returns its features as list
    '''
    assert os.path.exists(path), "Path to geojson doesnt exsits"
    with open(path) as f:
        data = json.load(f)
        assert "features" in data.keys(), "GeoJSON Contains No Features"
        features = data["features"]
    return features

def extract_coordinates(coordinates, type):
    ''' Takes the ['geometry']['coordinates'] Attribute of an geojson and
    returns a list of tupels with the coordinate pairs
    Note Multi features have to be split up and each part has to be delivered individually
    '''
    if "Point" in type:
        return [coordinates]
    if "LineString" in type:
        return coordinates
    if "Polygon" in type:
        return coordinates[0]


def get_bbox(features):
    '''this function returns a boundingbox for a geojson
    # it simply requieres a the features of the geojson !not the hole geojson
    '''
    assert isinstance(features, list), "features is not of type list/ no valid geojson"
    assert len(features) > 0, "no features contained in geojson"
    coordinates = []
    for feature in features:
        if "Multi" in feature["geometry"]["type"]:
            for part in feature["geometry"]["coordinates"]:
                coordinates += extract_coordinates(part, feature["geometry"]["type"])
        else:
            coordinates += extract_coordinates(feature["geometry"]["coordinates"]
                                               , feature["geometry"]["type"])
    x_coordinates = [c[0] for c in coordinates]
    y_coordinates = [c[1] for c in coordinates]
    return [min(x_coordinates), min(y_coordinates),
            max(x_coordinates), max(y_coordinates)]
