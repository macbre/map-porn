#!/usr/bin/env python3
import logging
import json
from dataclasses import dataclass
from os import path

from shared import Node, get_http_client

import requests

DIR = path.abspath(path.dirname(__file__))

# https://www.ssl.fo/fo/ferdaaetlan/hvar-er-bussurin-beint-nu/

# https://buscms.sona.fo/v2/areas/ -> all operators
# https://buscms.sona.fo/v2/areas/1 -> routes
# https://buscms.sona.fo/v2/routes/32 -> the route
BASE_URL = 'https://buscms.sona.fo/v2'


def fetch_json(url: str) -> object:
    """
    """
    url = BASE_URL + url

    logger = logging.getLogger(name="http")
    resp = get_http_client().get(url)
    resp.raise_for_status()

    logger.info(f'HTTP {resp.status_code} {url}')

    try:
        logger.debug(f'Resp: {resp.text}')
        return json.loads(resp.text)
    except json.JSONDecodeError:
        logging.error('Parsing the response failed', exc_info=True)
        raise


def main():
    logger = logging.getLogger(name="ssl")

    # prepare the list of nodes
    nodes: list[Node] = []

    logger.info('Getting the list of operators ...')

    # {"id":1,"name":"Tórshavn", ...  "updated_at":"2022-03-29T07:25:40.095Z"}
    opetators = map(
        lambda item: dict(id=item['id'], name=item['name']),
        fetch_json('/areas')
    )

    # iterate over operators: Tórshavn, Klaksvík, Sunda Kommuna, SSL
    for operator in opetators:
        logger.info(f'Processing opetator: {operator} ...')

        routes = fetch_json(f'/areas/{operator["id"]}')['routes']

        for route in routes:
            # name: "Leið 1: Tórshavn",
            logger.info(f'Processing route: {route["name"]} (id #{route["id"]}) ...')

            # https://buscms.sona.fo/v2/routes/32
            stops = fetch_json(f'/routes/{route["id"]}')['stations']

            nodes.extend(
                # e.g. Node(lat=62.25408443, lon=-6.529764124, tags=[('name', '43 Viðurbyrgi'), ('operator', 'Klaksvík')])
                Node(
                    lat=stop['lat'],
                    lon=stop['lng'],
                    tags=[
                        ('name', stop['name']),
                        ('operator', operator['name'])
                    ]
                )
                for stop in stops
            )

    # write the JSON
    logger.info(f'Collected {len(nodes)} nodes with bus stops')
    # print(nodes)

    geojson_file = path.join(DIR, '..', 'geojson', 'sona-busses.json')
    logger.info(f'Writing {len(nodes)} node(s) GeoJSON to {geojson_file} ...')

    with open(geojson_file, 'wt') as f:
        # f.write('const points = ')
        json.dump(
            {
                'type': 'FeatureCollection',
                'features': [
                    node.to_geojson()
                    for node in nodes
                ],
            },
            fp=f,
            indent=True
        )

    logger.info('Done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
