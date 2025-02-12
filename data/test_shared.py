from shared import Node, LineString


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

def test_line_string():
    line_string = LineString(
        coordinates=[
            [-7.0233513135463,62.13244487531483],[-7.023534458130598,62.13259667158127],[-7.023605788126588,62.132800268009305]
        ],
        tags=(
            ('summary', 'The hike between Saksun and Hald\u00f3rsv\u00edk is beautiful'),
            ('distance', '7500'),
            ("difficulty", '2')
        )
    )

    assert line_string.get('distance') == '7500'

    geojson = line_string.to_geojson()

    assert geojson['type'] == 'Feature'

    assert geojson['geometry']['type'] == 'LineString'
    assert geojson['geometry']['coordinates'] == line_string.coordinates

    assert geojson['properties']['distance'] == '7500'
