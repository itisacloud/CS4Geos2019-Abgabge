"""
a function to grab OSM data based on input features
"""
import requests
from src.utils_geojson import get_bbox

def grab_osm_data(osm_data, features):
    """ Takes input Features and search criteria and returns OSM data
    """
    return_features = []
    for feature in features:
        bbox = get_bbox([feature])
        path = 'https://api.ohsome.org/v0.9/elements/geometry'
        data = {'bboxes': ",".join(str(coord) for coord in bbox),
                'keys': ",".join(osm_data['keys']),
                'values': ",".join(osm_data['values']),
                'types': ",".join(osm_data['types']),
                'time': f'{osm_data["time"]}',
                'format': 'geojson',
                'properties': 'tags',
                'showMetadata': 'false'}

        response = requests.post(path, data=data)
        if not response.ok:
            print("Something with your request went wrong")
            print("please ensure a correct input in the config file")
        result = response.json()
        for test_feature in result["features"]:
            if test_feature in return_features:
                result["feature"].remove(test_feature)
        return_features += result["features"]
    print("recieved {} features".format(len(return_features)))
    return return_features
