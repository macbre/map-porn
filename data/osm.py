#!/usr/bin/env python3
import bz2
import logging
import json
import subprocess

from posixpath import dirname
from tempfile import gettempdir
from dataclasses import dataclass
from os import path
from typing import Iterator
from xml import sax
from xml.sax import handler, xmlreader

from shared import Node, nodes_to_geojson_collection, get_http_client, get_wikidata_claims


DIR = path.abspath(path.dirname(__file__))

# can be set for additional OR query on the nodes
EXTRA_TAG_KEY = None
EXTRA_TAG_VALUE = None

# https://wiki.openstreetmap.org/wiki/Category:Tag_descriptions

# https://wiki.openstreetmap.org/wiki/Buses#Stops_and_bus_stations
# <tag k="highway" v="bus_stop"/>
# Some mappers use bus=yes with public_transport=platform to specify a bus stop,
# instead of or in addition to highway=bus_stop
# TAG_KEY = 'bus'
# TAG_VALUE = 'yes'

# https://wiki.openstreetmap.org/wiki/Tag:aeroway%3Dhelipad
# <tag k="aeroway" v="helipad"/>
# TODO: handle <way> tags
# TAG_KEY = 'aeroway'
# TAG_VALUE = 'helipad'

# https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dferry_terminal
# <tag k="amenity" v="ferry_terminal"/>
# TAG_KEY = 'amenity'
# TAG_VALUE = 'ferry_terminal'

# https://wiki.openstreetmap.org/wiki/Tag:barrier%3Dcattle_grid
# TAG_KEY = 'barrier'
# TAG_VALUE = 'cattle_grid'

# https://wiki.openstreetmap.org/wiki/Tag:diplomatic%3Dconsulate
# TAG_KEY = 'diplomatic'
# TAG_VALUE = 'consulate'

# https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dlighthouse
# <tag k="man_made" v="lighthouse"/>
# TAG_KEY = 'man_made'
# TAG_VALUE = 'lighthouse'
# <tag k="seamark:type" v="light_minor"/>
# <tag k="seamark:type" v="light_major"/>
# EXTRA_TAG_KEY = 'seamark:type'
# EXTRA_TAG_VALUE = None

# https://wiki.openstreetmap.org/wiki/Tag:highway%3Dtraffic_signals
# <tag k="highway" v="traffic_signals"/>
# TAG_KEY = 'highway'
# TAG_VALUE = 'traffic_signals'

# https://wiki.openstreetmap.org/wiki/Tag:junction%3Droundabout
# TAG_KEY = 'junction'
# TAG_VALUE = 'roundabout'

# https://wiki.openstreetmap.org/wiki/Tag:leisure%3Dpitch
# <tag k="leisure" v="pitch"/>
# <tag k="sport" v="soccer"/>
# TAG_KEY = 'sport'
# TAG_VALUE = 'soccer'

# https://wiki.openstreetmap.org/wiki/Key:railway
# <tag k="railway" v="narrow_gauge"/>
# <tag k="railway" v="funicular"/>
# TAG_KEY = 'railway'
# TAG_VALUE = 'narrow_gauge'
# EXTRA_TAG_KEY = 'railway'
# EXTRA_TAG_VALUE = None

# https://wiki.openstreetmap.org/wiki/Tag:landuse%3Dforest
# <tag k="landuse" v="forest"/>
# TAG_KEY = 'landuse'
# TAG_VALUE = 'forest'

# https://wiki.openstreetmap.org/wiki/Tag:power=plant
# <tag k="power" v="plant"/>
# TAG_KEY = 'power'
# TAG_VALUE = 'plant'

# https://wiki.openstreetmap.org/wiki/Tag:building=church
# TAG_KEY = 'building'
# TAG_VALUE = 'church'

# https://wiki.openstreetmap.org/wiki/Tag:amenity=cinema
# https://www.cinematour.com/theatres/fo/FO/1.html
# TAG_KEY = 'amenity'
# TAG_VALUE = 'cinema'

# https://wiki.openstreetmap.org/wiki/Tag:amenity=pub
# https://wiki.openstreetmap.org/wiki/Tag:amenity=bar
# TAG_KEY = 'amenity'
# TAG_VALUE = 'pub'
# EXTRA_TAG_KEY = 'amenity'
# EXTRA_TAG_VALUE = 'bar'

# https://wiki.openstreetmap.org/wiki/Tag:artwork_type=sculpture
# https://wiki.openstreetmap.org/wiki/Tag:artwork_type=statue
# TAG_KEY = 'artwork_type'
# TAG_VALUE = 'sculpture'
# EXTRA_TAG_KEY = 'artwork_type'
# EXTRA_TAG_VALUE = 'statue'

# https://wiki.openstreetmap.org/wiki/Tag:historic=memorial
# TAG_KEY = 'historic'
# TAG_VALUE = 'memorial'

# https://wiki.openstreetmap.org/wiki/Tag:sport=soccer
# https://www.wikidata.org/wiki/Q845610
# TAG_KEY = 'sport'
# TAG_VALUE = 'soccer'

# https://wiki.openstreetmap.org/wiki/Tag:tourism=museum
# https://www.openstreetmap.org/node/8443937222
# TAG_KEY = 'tourism'
# TAG_VALUE = 'museum'

# https://wiki.openstreetmap.org/wiki/Tag:waterway=stream
# https://www.openstreetmap.org/way/724580036
# TODO: save as lines instead of points
# TAG_KEY = 'waterway'
# TAG_VALUE = 'stream'
# https://wiki.openstreetmap.org/wiki/Tag:waterway=waterfall
# https://www.openstreetmap.org/node/5658226279
# TAG_KEY = 'waterway'
# TAG_VALUE = 'waterfall'

# https://wiki.openstreetmap.org/wiki/Tag:amenity=grave_yard
# https://www.openstreetmap.org/way/782638560
# https://www.openstreetmap.org/way/559502615
TAG_KEY = 'amenity'
TAG_VALUE = 'grave_yard'

# https://wiki.openstreetmap.org/wiki/Tag:landuse=cemetery
# This tag is used for a cemetery that isn't part of a place of worship. 
EXTRA_TAG_KEY = 'landuse'
EXTRA_TAG_VALUE = 'cemetery'


"""
This function fetches the osm.pbf ProtoBuf over HTTP, converts it into osm.bz2 XML file and caches it locally.

https://download.geofabrik.de/bz2.html

brew install osmium-tool
apt install osmium-tool

osmium cat myfile.osm.pbf -o myfile.osm.bz2
"""
def cache_osm_file():
    # https://download.geofabrik.de/europe/faroe-islands.html
    # URL = 'https://download.geofabrik.de/europe/faroe-islands-latest.osm.bz2'
    URL = 'https://download.geofabrik.de/europe/faroe-islands-latest.osm.pbf'

    PBF_FILE = path.join(DIR, 'osm-faroe-islands.pbf.bz2')
    LOCAL_FILE = path.join(DIR, 'osm-faroe-islands.xml.bz2')

    logger = logging.getLogger(name="fetch")

    if path.exists(LOCAL_FILE):
        logger.info(f'The cached OSM XML file exists at {LOCAL_FILE}')
        return LOCAL_FILE

    logger.info(f'The cached OSM XML not found at {LOCAL_FILE} -> fetching {URL} ...')

    resp = get_http_client().get(URL, headers={'user-agent': 'osm.py'})
    resp.raise_for_status()

    logger.info(f'HTTP {resp.status_code}')

    with open(PBF_FILE, "wb") as f:
        f.write(resp.content)

    # https://docs.python.org/3/library/subprocess.html#subprocess.run
    # osmium cat myfile.osm.pbf -o myfile.osm.bz2
    logger.info(f'Converting PBF file to osm.bz2 ...')

    resp = subprocess.run(["osmium", "cat", PBF_FILE, "-o", LOCAL_FILE])
    if resp.returncode is not 0:
        raise Exception(resp.stderr)

    logger.info(f'osm.bz2 file stored in {LOCAL_FILE}')
    return LOCAL_FILE


class OSMHandler(handler.ContentHandler):
    def __init__(self, node_callback: callable = None) -> None:
        """
        Can be optionally provided with a node callback
        that will be called at the end of processing each <node> tag.
        """
        self._reset()
        self.logger = logging.getLogger(name=self.__class__.__name__)

        # here we'll keep the references to <node> tags without any children
        # they're later referenced by <way> tags
        self.nodes_references: dict[str, Node] = {}
        self.nodes_counter = 0

        # this will be called on each <node> tag along with its tags
        # <way> tags will also call it with the first references <node> tag
        self.node_callback = node_callback

    def _reset(self, current_element: str = None):
        self.current_element = current_element
        self.attrs = {}
        self.tags = []

    def startElement(self, name: str, attrs: xmlreader.AttributesImpl):
        if name == 'osm':
            # <osm version="0.6" generator="osmium/1.14.0">
            self.logger.info(f'OSM XML starts here, generated by {attrs.get("generator", "n/a")}')

        elif name == 'bounds':
            # <bounds minlat="60.866318" minlon="-8.690197" maxlat="62.905232" maxlon="-5.515148"/>
            self.logger.info(f'OSM XML bounds: {repr(attrs.__dict__.get("_attrs"))}')

        # https://wiki.openstreetmap.org/wiki/Node#Structure
        elif name == 'node':
            # <node id="29023814" version="5" timestamp="2022-12-08T01:56:54Z" lat="61.5557547" lon="-6.8145764">
            self._reset(current_element='node')
            self.nodes_counter = self.nodes_counter + 1

            self.attrs = {
                'id': attrs['id'],
                'lat': attrs['lat'],
                'lon': attrs['lon'],
            }

        elif name == 'tag' and self.current_element in ['node', 'way']:
            # append tags as a tuple
            # <tag k="place" v="town"/>
            # e.g. ('highway', 'traffic_signals'), ('traffic_signals', 'traffic_lights')
            self.tags.append((attrs['k'], attrs['v']))

        elif name == 'way':
            """
            <node id="374178126" version="5" timestamp="2019-10-05T00:55:31Z" lat="62.0112091" lon="-6.7721186"/>
            (...)
            <way id="4965566" version="8" timestamp="2019-10-05T00:52:15Z">
                <nd ref="374178126"/>
                <nd ref="4321355681"/>
                <tag k="highway" v="residential"/>
                <tag k="name" v="Sverrisgøta"/>
                <tag k="oneway" v="yes"/>
                <tag k="surface" v="asphalt"/>
            </way>
            """
            self._reset(current_element='way')

            # now wait for the first <nd ref="374178126"/> tag

        elif name == 'nd' and self.current_element == 'way':
            if not self.attrs.keys():
                # this is the first <nd> child of the <way> tag
                # get the referenced node
                if referenced_node := self.nodes_references.get( attrs['ref'] ):
                    self.logger.debug(f'Found referenced node for #{attrs["ref"]}')

                    self.attrs = {
                        'id': attrs['ref'],
                        'lat': referenced_node.lat,
                        'lon': referenced_node.lon,
                    }

                else:
                    self.logger.debug(f'Cannot find referenced node for #{attrs["ref"]}')


    def endElement(self, name: str):
        """
        Call node_callback for each <node> and <way> tag
        """
        if name == 'node':
            if self.tags:
                self.logger.debug(f'{name} ({self.attrs}): {self.tags}')

                if self.node_callback:
                    self.node_callback(self.attrs, self.tags)
            else:
                # register a node reference
                # as this <node> does not have any tags defined, it will be highly likely referenced by <way>
                self.logger.debug(f'{name} #{self.attrs["id"]} reference stored')

                self.nodes_references[ self.attrs['id'] ] = Node(
                    lat=self.attrs['lat'],
                    lon=self.attrs['lon'],
                    tags=[]
                )

            self._reset()

        elif name == 'way':
            if self.tags:
                self.logger.debug(f'{name} ({self.attrs}): {self.tags}')

                if self.node_callback:
                    self.node_callback(self.attrs, self.tags)

                self._reset()

    def endDocument(self):
        self.logger.info(f'Parsed OSM XML file with {self.nodes_counter} node(s) including')


def iterate_xml(xml_file, node_callback: callable):
    """
    Given a path to the local bz2-compressed OSM XML file parse it.
    """
    logger = logging.getLogger(name="xml")
    logger.info(f'Parsing OSM XML from {xml_file}')

    with bz2.open(xml_file) as f:
        # https://docs.python.org/3/library/xml.sax.reader.html
        reader = sax.make_parser(('xml.sax.xmlreader.IncrementalParser'))
        reader.setContentHandler(OSMHandler(node_callback))
        reader.parse(f)



def main():
    logger = logging.getLogger(name="osm")
    logger.info(f'Looking for "{TAG_KEY}" = "{TAG_VALUE}" ...')

    nodes: list[Node] = []

    def node_callback(node_attrs: dict[str, str], node_tags: list[tuple]):
        """
        This will be called for each parsed <node> tag
        """
        # <tag k="bus" v="yes"/>
        # <tag k="highway" v="bus_stop"/>
        matches = [
            (TAG_KEY, TAG_VALUE),
            (EXTRA_TAG_KEY, EXTRA_TAG_VALUE) if EXTRA_TAG_KEY is not None else None,
            # ('bus', 'yes'),)
        ]

        for (key, value) in node_tags:
            if (key, value) in matches:
                logger.info(f'Matching node found: {node_attrs} ({node_tags}')

                nodes.append(Node(
                    lat=node_attrs['lat'],
                    lon=node_attrs['lon'],
                    tags=node_tags
                ))

    local_file = cache_osm_file()
    iterate_xml(local_file, node_callback)

    # fetch more properties from WikiData if the field is present
    # "wikidata": "Q431648",
    # https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q431648&languages=en&props=claims&format=json
    for node in nodes:
        if node.get('wikidata') is not None:
            claims = {
                key: value
                for key, value in get_wikidata_claims(node.get('wikidata'))
            }
            node.tags.append(('wikidata_claims', claims))

    # write a GeoJSON file
    geojson_file = path.join(DIR, '..', 'geojson', f'osm-{TAG_KEY}-{TAG_VALUE}.json')
    logger.info(f'Writing {len(nodes)} node(s) GeoJSON to {geojson_file} ...')

    with open(geojson_file, 'wt') as f:
        json.dump(
            obj=nodes_to_geojson_collection(nodes),
            fp=f,
            indent=True
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
