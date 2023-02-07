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
FOLDER = 'lendiskort'
SERVICE = 'us_lendiskort'
MAP_ID = 48
LAYER = 'Tyrluplass'  # can be a substring match too

ACGIS_URL = f'https://gis.us.fo/arcgis/rest/services/{FOLDER}/{SERVICE}/MapServer/{MAP_ID}/query';

DIR = path.abspath(path.dirname(__file__))
GEOJSON_FILE = path.join(DIR, '..', 'geojson', f'us-{FOLDER}-{SERVICE}-{MAP_ID}-{LAYER}.json')


def filter_feature(feature: dict) -> bool:
    """
    Make get_features_from_arcgis() yield only the features we're interested in
    """
    props = feature.get('properties', {})
    layer = props.get('layer')
    return layer and LAYER in layer


def get_features_from_arcgis(url: str) -> Generator:
    """
    Yields a stream of geo features from provided ArcGIS service
    """
    logger = logging.getLogger('features')
    logger.info(f'Using <{url}> as a base')

    offset = 0

    while True:
        logger.info(f'Offset at #{offset}')

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
        yield from filter(filter_feature, features)

        # do we need to grab the next batch of data?
        # "exceededTransferLimit": true
        if data.get('exceededTransferLimit') is True:
            offset = offset + len(features)
            continue

        break

def main():
    logger = logging.getLogger('arcgis')
    logger.info(f'Using {FOLDER}/{SERVICE} with map #{MAP_ID} and "{LAYER}" layer filtering ...')

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
