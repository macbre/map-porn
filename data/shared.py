"""
Some share utilities
"""
from dataclasses import dataclass
import requests

@dataclass
class Node:
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
            "properties": {
                # e.g. ('name', '43 Viðurbyrgi')
                key: value
                for (key, value) in self.tags 
            }
        }


def nodes_to_geojson_collection(nodes: list[Node]) -> dict:
    """
    Return a valid GeoJSON structure with all the provided nodes
    """
    return {
        'type': 'FeatureCollection',
        'features': [
            node.to_geojson()
            for node in nodes
        ],
    }


_http_client = None

def get_http_client() -> requests.Session:
    """
    https://requests.readthedocs.io/en/latest/user/advanced/
    """
    global _http_client

    if _http_client is None:
        _http_client = requests.Session()
        _http_client.headers.update({'user-agent': 'python (https://github.com/macbre/map-porn)'})

    return _http_client
