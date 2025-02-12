#!/usr/bin/env python3
import logging
import json
import re

from dataclasses import dataclass
from os import path
from typing import Iterable

from shared import Node, get_http_client, nodes_to_geojson_collection

DIR = path.abspath(path.dirname(__file__))

# https://visitfaroeislands.com/en/whatson/hiking
# browser console: Array.from(Spruce.store("app").list.values())[0]

BASE_URL = 'https://visitfaroeislands.com/en/whatson/hiking'

@dataclass
class Hike:
    """
    A bit of typing for the huge JSON that visitfaroeislands.com provides
    """
    # headline: "Skálafjørður – Selatrað"
    # type: "hike"
    # url_slug: "skalafjordur-selatrad"
    # distance: 5600
    headline: str
    type: str
    url_slug: str
    distance: int


def get_hikes() -> Iterable[Hike]:
    url = BASE_URL

    logger = logging.getLogger(name="http")
    resp = get_http_client().get(url='https://visitfaroeislands.com/en/whatson/hiking')
    resp.raise_for_status()

    logger.info(f'HTTP {resp.status_code} {resp.url}')

    # .apply([],JSON.parse( "[[ ... ]]" ))
    raw_json: str = re.search(r'\.apply\(\[\],JSON\.parse\( "\[\[(.*)\]\]" \)\)', resp.text).group(1)

    raw_json = f'{raw_json}'

    # unescape JSON
    # \"type\":\"hike\"
    # {"type":"hike"
    raw_json = raw_json \
        .replace('\\"', '"') \
        .replace('\\\\u', '\\u') \
        .replace(',[{"type":"hike"', '\n[{"type": "hike"') \
        .replace(',{"type":"hike"', '\n{"type":"hike"')
    
    with open('/tmp/fo_trails.jsonl', 'wt') as fp:
        fp.write(raw_json)

    logger.info(f'JSON: {raw_json[:100]}...{raw_json[-100:]}')

    # treat as nd+json
    for line in raw_json.split('\n'):
        try:
            parsed = json.loads(line)
            yield Hike(headline=parsed['headline'], type=parsed['type'], url_slug=parsed['url_slug'], distance=parsed['distance'])

        except json.JSONDecodeError as ex:
            # logging.error(f'Parsing the JSON-encoded line failed around: {line[ex.colno-20:ex.colno+20]}', exc_info=True)
            pass


def main():
    logger = logging.getLogger(name="fo_trails")

    # prepare the list of nodes
    nodes: list[Node] = []

    logger.info('Getting the list of hikes ...')

    # iterate over hikes
    for idx, hike in enumerate(get_hikes()):
        # headline: "Skálafjørður – Selatrað"
        # type: "hike"
        # url_slug: "skalafjordur-selatrad"
        # distance: 5600
        logger.info(f'Processing hike #{idx+1}: {hike.headline} ({hike.distance} m long) - {hike.url_slug} ...')
        '''
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
            '''

    '''
    # write the JSON
    logger.info(f'Collected {len(nodes)} nodes with bus stops')
    # print(nodes)

    geojson_file = path.join(DIR, '..', 'geojson', 'sona-busses.json')
    logger.info(f'Writing {len(nodes)} node(s) GeoJSON to {geojson_file} ...')

    with open(geojson_file, 'wt') as f:
        json.dump(
            obj=nodes_to_geojson_collection(nodes),
            fp=f,
            indent=True
        )
    '''
    logger.info('Done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
