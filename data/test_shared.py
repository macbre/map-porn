import json
from shared import Node


TEST_LAT = 61.5257422
TEST_LON = -6.879629


def get_test_node() -> Node:
    return Node(
        lat=TEST_LAT,
        lon=TEST_LON,
        tags=(
            ('foo', 'bar'),
        )
    )


def test_node():
    node = get_test_node()

    assert node.lat == TEST_LAT
    assert node.lon == TEST_LON

    assert repr(node) == '<Node> 61.5257422, -6.879629'


def test_node_to_json():
    node = get_test_node()
    geojson = node.to_geojson()

    assert geojson['type'] == 'Feature'

    assert geojson['geometry']['type'] == 'Point'
    assert geojson['geometry']['coordinates'] == [TEST_LON, TEST_LAT]

    assert geojson['properties']['foo'] == 'bar'


def test_node_get():
    node = get_test_node()

    assert node.get('not_existing_property') is None
    assert node.get('foo') == 'bar'
