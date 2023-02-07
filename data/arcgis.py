#!/usr/bin/env python3
"""
This script takes the data from ArcGIS server and produces a complete GeoJSON file
"""
import json
import logging
from os import path
from typing import Generator
import requests

# https://gis.us.fo/arcgis/rest/services/lendiskort/us_lendiskort/MapServer/48
# FOLDER = 'lendiskort'
# SERVICE = 'us_lendiskort'
# MAP_ID = 48
# PROPETY_NAME = 'layer'
# PROPERTY_VALUE = 'Tyrluplass'  # can be a substring match too


# https://gis.us.fo/arcgis/rest/services/poi/us_poi/MapServer/layers
FOLDER = 'poi'
SERVICE = 'us_poi'
MAP_ID = 19
PROPERTY_NAME = 'poi_icon'
PROPERTY_VALUE = 'church'  # "poi_icon": "church",

ACGIS_URL = f'https://gis.us.fo/arcgis/rest/services/{FOLDER}/{SERVICE}/MapServer/{MAP_ID}/query';

DIR = path.abspath(path.dirname(__file__))
GEOJSON_FILE = path.join(DIR, '..', 'geojson', f'us-{FOLDER}-{SERVICE}-{MAP_ID}-{PROPERTY_VALUE or "main"}.json')


def filter_feature(feature: dict) -> bool:
    """
    Make get_features_from_arcgis() yield only the features we're interested in
    """
    # no PROPETY_NAME provided, no filtering then
    if PROPERTY_NAME is None:
        return True

    props = feature.get('properties', {})
    prop_value = props.get(PROPERTY_NAME)
    return prop_value and PROPERTY_VALUE in prop_value


def from_polygon_to_point(feature: dict) -> dict:
    """
    Save some space -> turn polygons into points (use the first coordinate)

    from
    {
      "type": "Feature",
      "id": 3806,
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -7.286266996565066,
              62.0656602855875
            ],
    (...)

    info

    "geometry": {
        "type": "Point",
        "coordinates": [
            -6.522042,
            62.2978137
        ]
    }
    """
    geometry_type = feature.get('geometry', {}).get('type')
    if geometry_type != 'Polygon':
        return feature

    polygon_points = feature.get('geometry', {}).get('coordinates')
    if not polygon_points:
        return feature

    feature['geometry'] = {
        "type": "Point",
        "coordinates": polygon_points[0][0]
    }

    return feature


def get_features_from_arcgis(url: str) -> Generator:
    """
    Yields a stream of geo features from provided ArcGIS service
    """
    logger = logging.getLogger('features')
    logger.info(f'Using <{url}> as a base')

    offset = 0

    while True:
        logger.info(f'Offset at #{offset}')

        # e.g. https://gis.us.fo/arcgis/rest/services/adressur/us_adr_husanr/FeatureServer/0/query
        query_params = {
            'f': 'geojson',
            'where': '1=1',
            'outFields': '*',
            'resultOffset': offset
        }

        resp = requests.get(url, headers={'user-agent': 'acrgis.py'}, params=query_params)
        resp.raise_for_status()

        # e.g. https://gis.us.fo/arcgis/rest/services/lendiskort/us_lendiskort/MapServer/48/query?where=1%3D1&geometryType=esriGeometryEnvelope&geometryPrecision=6&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=2000&returnGeometry=true&returnZ=false&returnM=false&returnIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&returnTrueCurves=false&returnExtentsOnly=false&f=geojson
        data = json.loads(resp.text)

        features = data.get('features', [])

        # filter features and turn polygons into a single points -> yield
        yield from map(
            from_polygon_to_point,
            filter(filter_feature, features)
        )

        # do we need to grab the next batch of data?
        # "exceededTransferLimit": true
        if data.get('exceededTransferLimit') is True:
            offset = offset + len(features)
            continue

        break

def main():
    logger = logging.getLogger('arcgis')
    logger.info(f'Using {FOLDER}/{SERVICE} with map #{MAP_ID} and "{PROPERTY_NAME}" = "{PROPERTY_VALUE}" filtering ...')
    logger.info(f'Features will be stored in {GEOJSON_FILE}')

    features = list(get_features_from_arcgis(ACGIS_URL))

    with open(GEOJSON_FILE, 'wt') as f:
        json.dump(
            {
                'type': 'FeatureCollection',
                'features': features,
            },
            fp=f,
            indent=True
        )

    logger.info(f'GeoJSON data stored in {GEOJSON_FILE} with {len(features)} features')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
