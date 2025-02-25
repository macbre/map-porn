#!/usr/bin/env python3
"""
This script takes the GeoJSON data from ArcGIS server and produces a complete GeoJSON file

https://gis.us.fo/arcgis/rest/services/adressur/us_adr_husanr_litir/MapServer/1/query?f=geojson&where=UPPER(street_city)%20LIKE%20%27%25%27&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=street_city%2COBJECTID&resultRecordCount=2500&resultOffset=2000
"""
import json
import logging

from collections import Counter
from os import path
from typing import Iterable, Optional

from shared import get_http_client


ARCGIS_SERVER = 'gis.us.fo'

# https://gis.us.fo/arcgis/rest/services/adressur/us_adr_husanr_litir/MapServer/1
FOLDER = 'adressur'
SERVICE = 'us_adr_husanr_litir'
MAP_ID = 1
PROPERTY_VALUE = 'most_common_streets'
WHERE = "UPPER(street_city) LIKE '%'"  # not empty street name


ACGIS_URL = f'https://{ARCGIS_SERVER}/arcgis/rest/services/{FOLDER}/{SERVICE}/MapServer/{MAP_ID}/query';

DIR = path.abspath(path.dirname(__file__))
GEOJSON_FILE = path.join(DIR, '..', 'geojson', f'us-{FOLDER}-{SERVICE}-{MAP_ID}-{PROPERTY_VALUE or "main"}.json')


class ArcGisError(Exception):
    pass


def get_features_from_arcgis(url: str) -> Iterable[dict]:
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
            'where': WHERE or '*',  # 
            'returnGeometry': 'true',
            'outFields': '*',
            'resultOffset': offset,
            'resultRecordCount': 1000,
        }

        resp = get_http_client().get(url, params=query_params)
        resp.raise_for_status()

        # e.g. https://gis.us.fo/arcgis/rest/services/lendiskort/us_lendiskort/MapServer/48/query?where=1%3D1&geometryType=esriGeometryEnvelope&geometryPrecision=6&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=2000&returnGeometry=true&returnZ=false&returnM=false&returnIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&returnTrueCurves=false&returnExtentsOnly=false&f=geojson
        try:
            data: dict = json.loads(resp.text)
        except json.JSONDecodeError:
            logger.error(f'JSON decoding failed, got: {resp.text}', exc_info=True)
            raise

        # report errors (they come as HTTP 200 response, yikes!)
        error: Optional[dict] = data.get('error')

        if error:
            message = error.get('message')
            logger.error(f'Request error: {message}')
            raise ArcGisError(message)

        features = data.get('features', [])

        yield from features

        # do we need to grab the next batch of data?
        # "exceededTransferLimit": true
        if data.get('exceededTransferLimit') is True:
            offset = offset + len(features)
            continue

        break

def main():
    logger = logging.getLogger('arcgis')
    logger.info(f'Using {FOLDER}/{SERVICE} with map #{MAP_ID}')
    logger.info(f'Features will be stored in {GEOJSON_FILE}')


    # first pass: collect the most common street names
    # street_name	"Oman Rygg"
    # street_city	"Oman Rygg, Fuglafjørður"
    street_city_unique: set[str] = set()

    for feature in get_features_from_arcgis(ACGIS_URL):
        # collect the unique <street>, <city> entries
        street_city = dict(feature.get('properties', {})).get('street_city')

        if street_city:
            street_city_unique.add(street_city)

    # now, extract street names from the pairs and prepare the list of the most common ones
    street_names = Counter()

    for entry in street_city_unique:
        street_name = entry.split(',')[0] if ',' in entry else None

        if street_name:
            street_names[street_name] += 1
        else:
            logger.warning(f'Street "{entry}" misses the city info')

    logger.info(f'Most common street names {repr(street_names.most_common(10))}')

    # second pass: keep only the most common streets
    most_common = [value for (value, _) in street_names.most_common(5)]

    features = [
        feature
        for feature in get_features_from_arcgis(ACGIS_URL)
        if dict(feature.get('properties', {})).get('street_name') in most_common
    ]

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
    logging.basicConfig(level=logging.DEBUG)
    main()
