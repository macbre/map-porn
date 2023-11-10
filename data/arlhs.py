#!/usr/bin/env python3
import logging
import json
import re
from os import path
from typing import Iterable

from shared import Node, get_http_client, nodes_to_geojson_collection

import requests

DIR = path.abspath(path.dirname(__file__))

# http://wlol.arlhs.com/index.php?mode=zones&zone=FAR
BASE_URL = 'http://wlol.arlhs.com'
ZONE = 'FAR'


def iterate_lighthouses(zone: str) -> Iterable[Node]:
    logger = logging.getLogger(name="lighthouses")

    resp = get_http_client().get(f'{BASE_URL}/index.php', params={'mode': 'zones', 'zone': zone})
    resp.raise_for_status()

    print(resp.url)

    # <td nowrap><a href="/lighthouse/FAR1.html">FAR 001</a>
    for match in re.finditer(r'<td nowrap><a href="\/lighthouse\/([^"]+)">', resp.text):
        page = match.group(1)
        logger.info(f'Parsing the /lighthouse/{page} subpage ...')

        resp = get_http_client().get(f'{BASE_URL}/lighthouse/{page}')
        resp.raise_for_status()

        # parse the geoloc data
        # new google.maps.LatLng(62.199998771124, -6.6999997880168);
        matches = re.search(r'LatLng\(([\d\-.]+), ([\d\-.]+)\)', resp.text)

        if matches is None:
            logger.warning('Not geolocation data found on the page')
            continue

        # <h1 class="lightname">Lervig Light</h1>
        name = re.search(r'<h1 class="lightname">([^<]+)</h1>', resp.text)
        
        # <h2 class="lightname">ARLHS FAR-018</h2>
        code = re.search(r'<h2 class="lightname">([^<]+)</h2>', resp.text)

        yield Node(
            lat=matches.group(1),
            lon=matches.group(2),
            tags=(
                ('name', name.group(1)),
                ('code', code.group(1)),
                ('url', resp.url),
            )
        )
        


def main():
    logger = logging.getLogger(name="arlhs")

    # prepare the list of nodes
    nodes: list[Node] = []

    logger.info(f'Getting the list of lighthouses in {ZONE} ...')

    for lighthouse in iterate_lighthouses(ZONE):
        logger.info(lighthouse)
        nodes.append(lighthouse)


    # write the JSON
    logger.info(f'Collected {len(nodes)} lightouses')
    # print(nodes)

    geojson_file = path.join(DIR, '..', 'geojson', f'arlhs-{ZONE}.json')
    logger.info(f'Writing {len(nodes)} node(s) GeoJSON to {geojson_file} ...')

    with open(geojson_file, 'wt') as f:
        json.dump(
            obj=nodes_to_geojson_collection(nodes),
            fp=f,
            indent=True
        )

    logger.info('Done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
