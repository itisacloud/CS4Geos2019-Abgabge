# CS4Geos2019-Abgabge
Landsat and Sentinel frequently capture date of the earths surface. Those can be used to calculate the NDVI(Normalized Diffrence Vegitation Index).
This rogramm can calculate the NDVI for multiple features over a defined span of time, to analyse its temporal spatial relations.

## Requierements
Python Version 3.3+
external libaries:
1. rasterio (install via: conda install rasterio or pip install rasterio)
2. shapely  (install via: conda install shapely or pip install shapely)
3. pyproj (install via: pip install pyproj)
4. satsearch (install via: pip install rasterio)
5. numpy (install via: conda install numpy or pip install numpy)
6. matplotlib (install via : conda install matplotlib or pip install matplotlib)

## Installation
From source repository:
$ git clone https://github.com/itisacloud/CS4Geos2019-Abgabge.git

## Usage 
Running this script requieres a config file in form of a json. An example is given with heidelberg.json, in which you 
define all the input parameters. In addition you need to provide an
input .geojson (you can quickly create one via geojson.io for example), which contains your area of intrest.
If the osm parameter is set true you can define an query for downloading OSM features via the OHSOME API.
You can decide if you want to show Plots of the results or generate an output geojson for further usage.
