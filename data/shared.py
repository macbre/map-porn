"""
Some share utilities
"""
import logging
from dataclasses import dataclass
from typing import Any, Optional, Iterator

from requests import Session 


class GeoJsonBase:
    tags: list[tuple[str, str]]

    def get(self, name: str) -> Optional[Any]:
        for (key, value) in self.tags:
            if key == name:
                return value
        return None

    def get_properties(self) -> dict[str, str]:
        return {
            # e.g. ('name', '43 Viðurbyrgi')
            key: value
            for (key, value) in self.tags
        }


@dataclass
class Node(GeoJsonBase):
    lat: str
    lon: str
    tags: list[tuple[str, str]]

    def to_geojson(self) -> dict:
        """
        Emits GeoJSON-compatible entry

        @see https://geojson.org/
        @see https://geojson.io/
        """
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(self.lon), float(self.lat)]
            },
            "properties": self.get_properties()
        }

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}> {self.lat}, {self.lon}'


@dataclass
class LineString(GeoJsonBase):
    tags: list[tuple[str, str]]

    # {"type":"LineString","coordinates":[[-6.53700839728117,62.205172553658485], ...
    coordinates: list[list[float]]

    def to_geojson(self) -> dict:
        """
        Emits GeoJSON-compatible entry

        @see https://geojson.org/
        @see https://geojson.io/
        """
        return {
            "type": "Feature",
            "geometry": {
                # https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.4
                "type": "LineString",
                "coordinates": self.coordinates,
            },
            "properties": self.get_properties()
        }

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}> [{self.coordinates[0]}, ...]'



def nodes_to_geojson_collection(nodes: list[Node]) -> dict:
    """
    Return a valid GeoJSON structure with all the provided nodes
    """
    return {
        'type': 'FeatureCollection',
        'features': [
            node.to_geojson()
            for node in nodes
            # if float(node.lat) < 61.56  # temp filtering
        ],
    }


_http_client = None

def get_http_client() -> Session:
    """
    https://requests.readthedocs.io/en/latest/user/advanced/
    """
    global _http_client

    if _http_client is None:
        _http_client = Session()
        _http_client.headers.update({'user-agent': 'python (https://github.com/macbre/map-porn)'})

    return _http_client


def get_wikidata_claims(entity: str) -> Iterator[tuple[str, dict]]:
    """
    E.g. 'Q431648'

    https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q431648&languages=en&props=claims&format=json
    """
    logger = logging.getLogger('wikidata')
    logger.info(f'Getting claims for the {entity} entity')

    resp = get_http_client().get('https://www.wikidata.org/w/api.php', params={
        'ids' : entity,
        'action': 'wbgetentities',
        'languages': 'en',
        'props': 'claims',
        'format': 'json',
    })
    resp.raise_for_status()

    entities: dict = resp.json().get('entities', {})
    entity: dict = list(entities.values())[0]
    claims: dict = entity.get('claims', {})

    for property, claim in claims.items():
        # P17 -> {'entity-type': 'item', 'numeric-id': 4628, 'id': 'Q4628'}
        # print(property, claim[0]['mainsnak']['datavalue']['value'])

        try:
            value = claim[0]['mainsnak']['datavalue']['value']
            yield property, value
        except KeyError:
            pass

