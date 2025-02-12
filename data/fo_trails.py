#!/usr/bin/env python3
import logging
import json
import re

from dataclasses import dataclass
from os import path
from typing import Iterable

from shared import LineString, get_http_client, nodes_to_geojson_collection

DIR = path.abspath(path.dirname(__file__))

# https://visitfaroeislands.com/en/whatson/hiking
# browser console: Array.from(Spruce.store("app").list.values())[0]
BASE_URL = 'https://visitfaroeislands.com/en/whatson/hiking'

@dataclass
class Hike:
    name: str
    description: str
    url: str
    # url_slug: "skalafjordur-selatrad"
    url_slug: str
    image: str
    geo_json: dict
    url_slug: str
    distance_km: int


def get_hikes() -> Iterable[Hike]:
    url = BASE_URL

    logger = logging.getLogger(name="get_hikes")
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
        .replace('\\\\u', '\\u')
    
    # find url_slus
    # "url_slug":"langasandur-streymnes1"
    for match in re.finditer(r'"url_slug":"([^"]+)"', raw_json):
        url_slug = match.group(1)

        # fetch the page

        # https://visitfaroeislands.com/en/whatson/hiking/hike/nordoyri-skuvadalur
        resp = get_http_client().get(url=f'https://visitfaroeislands.com/en/whatson/hiking/hike/{url_slug}')

        resp.raise_for_status()
        logger.info(f'HTTP {resp.status_code} {resp.url}')

        # var geoJson = {"type":"LineString","coordinates":[[-6.53700839728117,62.205172553658485], ...
        raw_json = re.search(r'({"type":"LineString","coordinates":[^}]+})', resp.text).group(1)
        geo_json = json.loads(raw_json)

        # TODO: parse meta
        # <meta property="og:title" content="Norðoyri - Skúvadalur" />
        # <meta property="og:description" content="A lovely trip to the scout house in Skúvadalur among sheep, birds and historical traces." />
        # <meta property="og:image" content="https://vfibackend.com/uploads/2023-06-01-skuvadalur-37-8w6a6439.jpg" />

        """
        <b data-overlay-text-target="distance_fact">
            5 km
        </b>
        """
        distance_km = int(re.search(r'"distance_fact">\s+(\d+) km\s+</b>', resp.text).group(1))

        yield Hike(
            url_slug=url_slug,
            url=resp.url,
            geo_json=geo_json,
            name='',
            description='',
            image='',
            distance_km=distance_km,
        )


def main():
    logger = logging.getLogger(name="fo_trails")

    # prepare the list of nodes
    nodes: list[LineString] = []

    logger.info('Getting the list of hikes ...')

    # iterate over hikes
    for idx, hike in enumerate(get_hikes()):
        # headline: "Skálafjørður – Selatrað"
        # type: "hike"
        # url_slug: "skalafjordur-selatrad"
        # distance: 5600
        logger.info(f'Processing hike #{idx+1}: {hike.name} {hike.url_slug} ({hike.distance_km} km) ...')

        coordinates = hike.geo_json.get('coordinates', [])
        assert len(coordinates) > 1, 'We need the route to have more than a single coordinate'

        nodes.append(
            LineString(
                coordinates=hike.geo_json.get('coordinates', []),
                tags=[
                    ('name', hike.name),
                    ('distance_km', hike.distance_km),
                    ('url', hike.url),
                    ('image', hike.image),
                ]
            )
        )

        # debug
        if idx > 5: break

    # write the JSON
    """
    All across the Faroe Islands, you'll find bygdagøtur – old village paths that have been in use since the islands were first settled.

    According to Faroese legislation walking on the in- and outfields require the landowners’ permission. You are only allowed to walk in this area with a guide. Hiking here without a guide can be fined.
    """
    logger.info(f'Collected {len(nodes)} nodes with hikes')

    geojson_file = path.join(DIR, '..', 'geojson', 'fo-hikes.json')
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
