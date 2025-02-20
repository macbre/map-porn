#!/usr/bin/env python3
"""
This script takes the data from ArcGIS server and produces a complete GeoJSON file
"""
import json
import logging
from os import path
from typing import Generator
import requests

from shared import get_http_client


NO_PAGINATION = False

ARCGIS_SERVER = 'gis.us.fo'
POLYGONS_TO_POINTS = True

# https://gis.us.fo/arcgis/rest/services/lendiskort/us_lendiskort/MapServer/48
# FOLDER = 'lendiskort'
# SERVICE = 'us_lendiskort'
# MAP_ID = 48
# PROPERTY_NAME = 'layer'
# PROPERTY_VALUE = 'tyrluplass'  # can be a substring match too


# https://gis.us.fo/arcgis/rest/services/poi/us_poi/MapServer/layers
# https://kort.foroyakort.fo/kort/
# FOLDER = 'poi'
# SERVICE = 'us_poi'
# MAP_ID = 19
# PROPERTY_NAME = 'poi_icon'
# PROPERTY_VALUE = 'bus'

# https://gis.us.fo/arcgis/rest/services/topo_20/us_topo20/MapServer/1184
# """
# "Oyggj": "Eysturoy",
# "Fjall": "Sl\u00e6ttaratindur",
# "Hadd": 880,
# """
# FOLDER = 'topo_20'
# SERVICE = 'us_topo20'
# MAP_ID = 1184
# PROPERTY_NAME = None
# PROPERTY_VALUE = None
# NO_PAGINATION = True

# https://gis.lv.fo/arcgis/rest/services/rulluportur/rulluportur_alment/MapServer
# ARCGIS_SERVER = 'gis.lv.fo'  # Landsverk
# FOLDER = 'rulluportur'
# SERVICE = 'rulluportur_alment'
# MAP_ID = 0
# PROPERTY_NAME = None
# PROPERTY_VALUE = 'cattle_grid'

# https://gis.us.fo/arcgis/rest/services/lendiskort/us_lendiskort/MapServer/43
# FOLDER = 'lendiskort'
# SERVICE = 'us_lendiskort'
# MAP_ID = 43
# PROPERTY_NAME = "tunnel"  # "tunnel": 1 // "under_construction": 1
# PROPERTY_VALUE = '1'

# https://gis.us.fo/arcgis/rest/services/matriklar/us_matr/MapServer?f=jsapi
# https://gis.us.fo/arcgis/rest/services/matriklar/us_matr/MapServer/2
# FOLDER = 'matriklar'
# SERVICE = 'us_matr'
# MAP_ID = 2
# PROPERTY_NAME = None
# PROPERTY_VALUE = "contour"

# https://gis.us.fo/arcgis/rest/services/lendiskort/us_lendiskort/MapServer/15
# FOLDER = 'lendiskort'
# SERVICE = 'us_lendiskort'
# MAP_ID = 15  # Oyggjar
# PROPERTY_NAME = None
# PROPERTY_VALUE = "oyggjar"
# POLYGONS_TO_POINTS = False  # keep the polygons as we need islands shapes

# https://gis.us.fo/arcgis/rest/services/bygdir/us_bygdir/MapServer
# FOLDER = 'bygdir'
# SERVICE = 'us_bygdir'
# MAP_ID = 0
# PROPERTY_NAME = None
# PROPERTY_VALUE = "bygdir"

# https://gis.us.fo/arcgis/rest/services/vegir/us_vegir_loyvda_ferd_vegt/MapServer/27
# https://www.arcgis.com/home/webmap/viewer.html?url=https%3A%2F%2Fgis.us.fo%2Farcgis%2Frest%2Fservices%2Fvegir%2Fus_vegir_loyvda_ferd_vegt%2FMapServer&source=sd
# i gert = ja
#  under_construction ( type: esriFieldTypeSmallInteger, alias: í gerð , Coded Values: [1: Ja] )
# FOLDER = 'vegir'
# SERVICE = 'us_vegir_loyvda_ferd_vegt'
# MAP_ID = 27
# PROPERTY_NAME = "under_construction"
# PROPERTY_VALUE = "1"
# POLYGONS_TO_POINTS = False

# https://gis.us.fo/arcgis/rest/services/vegir/us_hagagotur/MapServer
# trails between villages


# https://www.foroyakort.fo/tidindi/ferdsluhagtoel
# https://gis.lv.fo/arcgis/rest/services/ferdsla/ferdsluteljingar_alment/MapServer/1
# aadt - Annual Average Daily Traffic
# aawt - Average Annual Weekday Traffic: The average 24-hour traffic volume occurring on weekdays over a full year.
# https://archive.nptel.ac.in/content/storage2/courses/105101008/511_FundParams/point6/point.html
# 
# ARCGIS_SERVER = 'gis.lv.fo'  # Landsverk
# FOLDER = 'ferdsla'
# SERVICE = 'ferdsluteljingar_alment'
# MAP_ID = 0

# PROPERTY_NAME = None
# PROPERTY_VALUE = "ferdsla"

# https://gis.us.fo/arcgis/rest/services/ferdsla/us_ferdsluteljingar/MapServer/0
# https://www.landsverk.fo/fo-fo/borgari/fer%C3%B0sluteljara-hagtoel
# https://gis.us.fo/arcgis/rest/services/ferdsla/us_ferdsluteljingar/MapServer/0/query?where=1%3D1&f=pjson&outFields=*
FOLDER = 'ferdsla'
SERVICE = 'us_ferdsluteljingar'
MAP_ID = 0
PROPERTY_NAME = None
PROPERTY_VALUE = "ferdsla"

# https://gis.us.fo/arcgis/rest/services/sev/us_sev/MapServer/7
# FOLDER = 'sev'
# SERVICE = 'us_sev'
# MAP_ID = 7
# PROPERTY_NAME = None
# PROPERTY_VALUE = "vindmyllur"

# https://agisportal.sev.fo/arcgis/rest/services/Kortal/SEV/MapServer/4
# ARCGIS_SERVER = 'agisportal.sev.fo'
# FOLDER = 'Kortal'
# SERVICE = 'SEV'
# MAP_ID = 4
# PROPERTY_NAME = None
# PROPERTY_VALUE = "vindmylla"


# https://agisportal.sev.fo/arcgis/rest/services/Kortal/SEV/MapServer/3
ARCGIS_SERVER = 'agisportal.sev.fo'
FOLDER = 'Kortal'
SERVICE = 'SEV'
MAP_ID = 3
PROPERTY_NAME = None
PROPERTY_VALUE = "orkustod"


# https://gis.us.fo/arcgis/rest/services/foroya_tele/us_televarps_sendarar/MapServer/0
# icon: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAWCAYAAAA4oUfxAAAAAXNSR0IB2cksfwAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAU9JREFUSInF1j1ugzAUB/A/UkbugCw1vQFUjcoR6BZlaOduqM6SnqE5QuZ0iCxl6RGYmqVDIlVqkZAnLsBOJyIIfgYb0b4J+eP9/IwtmOAfYzJG0vn8IQIAId7eR8M976pUtR8OH1X/uU3K1LHGKch0fn0RWnwo2BVKfEw0DMOnJEk2LdwE5TzGbHYL3/fB2LQ3nuf5+VlZeZb99E5mGmmabrT4X4USv9xG13VxPH6S/VRk2TcAh5zTq/KiKHph7WhdbXNcFdW5UFV0eWai6B4AsFw+g/N4OF6H9K+hxOn0BQDgPG5sRQOXMnVs7jh9O0owdk3Os658tXrBev2qGaGHB+FC7CHEnqy6C1biplvP2BS73RZBcNNoU+XtxHUIdbgWi8e+aezwagE2oaqaxOuDbb9wFNiJ0wvxImpcENx1/jYZ482FSDK5lNIkFQDgF/YbdmsaqEFlAAAAAElFTkSuQmCC
# FOLDER = 'foroya_tele'
# SERVICE = 'us_televarps_sendarar'
# MAP_ID = 0
# PROPERTY_NAME = None
# PROPERTY_VALUE = "tv_transmitters"


# https://gis.torshavn.fo/arcgis/rest/services/vegir/ferdsla_alment/MapServer/6

# https://gis.lv.fo/arcgis/rest/services/gotuljos/gotuljos_alment/MapServer/layers
# ARCGIS_SERVER = 'gis.lv.fo'
# FOLDER = 'gotuljos'
# SERVICE = 'gotuljos_alment'
# MAP_ID = 0
# PROPERTY_NAME = None
# PROPERTY_VALUE = "gotuljos"



ACGIS_URL = f'https://{ARCGIS_SERVER}/arcgis/rest/services/{FOLDER}/{SERVICE}/MapServer/{MAP_ID}/query';

DIR = path.abspath(path.dirname(__file__))
GEOJSON_FILE = path.join(DIR, '..', 'geojson', f'us-{FOLDER}-{SERVICE}-{MAP_ID}-{PROPERTY_VALUE or "main"}.json')


class ArcGisError(Exception):
    pass


def filter_feature(feature: dict) -> bool:
    """
    Make get_features_from_arcgis() yield only the features we're interested in
    """
    # no PROPETY_NAME provided, no filtering then
    if PROPERTY_NAME is None:
        return True

    props = feature.get('properties', {})
    prop_value = str(props.get(PROPERTY_NAME))
    return prop_value and PROPERTY_VALUE in prop_value.lower()


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
    if POLYGONS_TO_POINTS is False:
        return feature

    geometry_type = feature.get('geometry', {}).get('type')
    if geometry_type != 'Polygon':
        # allow only lat, lon and elevation data
        feature['geometry']['coordinates'] = feature.get('geometry', {}).get('coordinates')[:3]

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
    logger.info(f'Using <{url}> as a base', extra={'pagination': NO_PAGINATION})

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

        # https://gis.us.fo/arcgis/rest/services/topo_20/us_topo20/MapServer/1184/query?f=geojson&where=1%3D1&outFields=%2A&resultOffset=0
        # Pagination is not supported.
        if NO_PAGINATION:
            del query_params['resultOffset']

        resp = get_http_client().get(url, params=query_params)
        resp.raise_for_status()

        # e.g. https://gis.us.fo/arcgis/rest/services/lendiskort/us_lendiskort/MapServer/48/query?where=1%3D1&geometryType=esriGeometryEnvelope&geometryPrecision=6&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=2000&returnGeometry=true&returnZ=false&returnM=false&returnIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&returnTrueCurves=false&returnExtentsOnly=false&f=geojson
        try:
            data = json.loads(resp.text)
        except json.JSONDecodeError:
            logger.error(f'JSON decoding failed, got: {resp.text}', exc_info=True)
            raise

        # report errors (they come as HTTP 200 response, yikes!)
        if error := data.get('error'):
            message = error.get('message')
            logger.error(f'Request error: {message}')
            raise ArcGisError(message)

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
    logging.basicConfig(level=logging.DEBUG)
    main()
