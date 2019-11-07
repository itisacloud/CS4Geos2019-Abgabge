''' These are functions written directly for the ndvi_main script
# the include generateing an list of geometries out of a the features of a geojson
# fetching the red and nir band out of an satsearch response for landsat or sentinel data
# creating a mask for a band based on geomtries and applying this mask to the band
# calculating the ndvi of two numpy arrays
'''
import sys
from functools import partial

import numpy as np
from pyproj import Proj, transform
from shapely.geometry import Point, Polygon, MultiPolygon,\
    MultiLineString, MultiPoint, LineString, asShape
from shapely.ops import transform as shtransform
import rasterio as rio



def get_url_pair(item, collection):
    '''# returns the right urls for the red and nir band for either landsat or sentinel
    # requieres the item and the requested collection
    '''
    if collection == 'landsat-8-l1':
        return [item.assets["B4"]["href"], item.assets["B5"]["href"]]
    return [item.assets["B04"]["href"], item.assets["B08"]["href"]]


def create_mask(geom_list, rows, cols, affine, origin_row,
                origin_col, crs):
    ''' creates a mask based on polygon features for a raster
    # requires the features in as dictionary and information related to the numpy array itself
    # + requires the get_geom_list function
    # + its spatial reference system
    # it returns a set of indexes in form of a list with the format of
    # list["feature"]["indexes for the feature"]
    '''
    id_list = []
    transformed_geom_list = geom_list = [transform_geometry(geom, crs) for geom in geom_list]
    for geom in range(len(transformed_geom_list)):
        id_list.append([])
    for row_id in range(rows):
        for col_id in range(cols):

            polygon = Polygon([affine * (col_id + origin_col, row_id + origin_row),
                               affine * (col_id + origin_col, row_id + origin_row+1),
                               affine * (col_id + origin_col+1, row_id + origin_row+1),
                               affine * (col_id + origin_col+1, row_id + origin_row)])
            for u, geom in enumerate(transformed_geom_list):
                if geom.intersects(polygon):
                    id_list[u].append([row_id, col_id])
    return id_list


def grab_values_by_mask(mask, band):
    ''' this function applies a set of indexes to an array
    #and returns all the values
    '''
    value_list = []
    for i in range(len(mask)):
        value_list.append([])
    for i, submask in enumerate(mask):

        for row_id, col_id in submask:
            try:
                value_list[i].append(band[row_id, col_id])
            except IndexError:
                continue
    return value_list


def transform_bounding_box(bbox, epsg_out):
    ''' transforms a boundingbox from epsg 4326 into a certain given crs
    # requieres the transform_coordinate function
    '''
    x_min1, y_min1, x_max1, y_max1 = bbox
    return transform_coordinate(x_min1, y_min1, epsg_out) \
        + transform_coordinate(x_max1, y_max1, epsg_out)


def transform_coordinate(x_1, y_1, epsg_out):
    ''' transforms a given coordinate pair from epsg 4326 into a given crs
    # requieres pyproj
    '''

    in_proj = Proj(init='epsg:4326')
    out_proj = Proj(init=epsg_out)
    x_2, y_2 = transform(in_proj, out_proj, x_1, y_1)
    return [x_2, y_2]


def transform_geometry(geometry, epsg_out):
    ''' Reprojects an input geometry into an output CRS'''
    project = partial(
        transform,
        Proj(init='epsg:4326'),
        Proj(init=epsg_out))
    return shtransform(project, geometry)


def get_geom_list(features, buffer_distance):
    ''' creates a list of geobetries based on an input geojson["features"]
    # requires shapely and the transform coordinate function
    # returns a list with all the geometries appended
    '''

    geom_list = []
    for feature_json in features:
        if feature_json["geometry"]["type"] == "MultiPolygon":
            polygons = []
            for part in feature_json["geometry"]["coordinates"]:

                if len(part)==1:
                    polygons.append(Polygon(part[0]))
                else:
                    polygons.append(Polygon(part[0], part[:1]))
            geom = MultiPolygon(polygons)
        elif feature_json["geometry"]["type"] == "MultiLineString":
            geom = MultiLineString([LineString(coord)
                                    for coord in feature_json["geometry"]["coordinates"]])
        elif feature_json["geometry"]["type"] == "MultiPoint":
            geom = MultiPoint([Point(coord) for coord in feature_json["geometry"]["coordinates"]])
        else:
            geom = asShape(feature_json["geometry"])
        if buffer_distance != 0:
            geom = geom.buffer(buffer_distance)
        geom_list.append(geom)
    print("Created  Geometry List")
    return geom_list


def download_band(url, bbox):
    ''' this function downloads and reads the requested band
    # to minimize the need of RAM, it utilizes the a rasterio window
    # it returns the band itself information about the spatial reference
    # [band, affine, int(row_end), int(col_start), crs]
    '''
    with rio.open(url) as src:
        affine = src.transform
        crs = src.crs.to_string()

        trans_bbox = transform_bounding_box(bbox, crs)
        col_start, row_start = ~affine * (trans_bbox[0], trans_bbox[1])
        col_end, row_end = ~affine * (trans_bbox[2], trans_bbox[3])
        band = src.read(1, window=((int(row_end), int(row_start)), (int(col_start), int(col_end))))
        assert band.shape != (0, 0), "Band has no Data(after window)"

    return [band, affine, int(row_end), int(col_start), crs]


def calculate_ndvi(red_band, nir_band):
    ''' this function calculates the ndvi values for to
    # numpy arrays, it filters all unrealistic values
    # and returns a list with all the values
    '''
    assert isinstance(red_band, np.ndarray), "Red band is not an Numpy Array"
    assert isinstance(nir_band, np.ndarray), "NIR band is not an Numpy Array"
    ndvi = (nir_band - red_band) / (nir_band + red_band)

    return ndvi
