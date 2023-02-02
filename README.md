# map-porn
Templates used to generate maps based on geo data for Faroe Islands and Ireland


## Resources

### [OSM XML snapshot for Faroe Islands](https://download.geofabrik.de/europe/faroe-islands.html)

* [`<node>` tag](https://wiki.openstreetmap.org/wiki/Node#Structure)
* [`<way>` tag](https://wiki.openstreetmap.org/wiki/Way#Examples)

```xml
$ cat faroe-islands-latest.osm.bz2 | bzip2 -d | head -n100
<?xml version='1.0' encoding='UTF-8'?>
<osm version="0.6" generator="osmium/1.14.0">
  <bounds minlat="61.3" minlon="-8" maxlat="63" maxlon="-6"/>
  <node id="29023724" version="3" timestamp="2016-06-27T08:58:38Z" lat="61.455746" lon="-6.7590335">
    <tag k="is_in" v="Sumba (Suðuroy), Føroyar"/>
    <tag k="name" v="Akrar"/>
    <tag k="place" v="village"/>
    <tag k="population" v="28"/>
    <tag k="postal_code" v="927"/>
    <tag k="wikidata" v="Q420746"/>
  </node>
  <node id="29023814" version="5" timestamp="2022-12-08T01:56:54Z" lat="61.5557547" lon="-6.8145764">
    <tag k="is_in" v="Tvøroyri (Suðuroy), Føroyar"/>
    <tag k="name" v="Tvøroyri"/>
    <tag k="place" v="town"/>
    <tag k="population" v="1195"/>
    <tag k="postal_code" v="800"/>
    <tag k="wikidata" v="Q754666"/>
  </node>
  (...)
  <node id="439361655" version="3" timestamp="2012-03-08T21:11:07Z" lat="62.2430899" lon="-6.8085287">
    <tag k="addr:city" v="Fuglafjørður"/>
    <tag k="addr:country" v="FO"/>
    <tag k="addr:housenumber" v="20"/>
    <tag k="addr:postcode" v="530"/>
    <tag k="addr:street" v="Bøvegur"/>
    <tag k="source" v="Umhvørvisstovan www.us.fo"/>
    <tag k="us.fo:Adressutal" v="30794"/>
    <tag k="us.fo:Galdandi_frá" v="12-12-2008"/>
    <tag k="us.fo:Postnr" v="530"/>
    <tag k="us.fo:Veganr" v="3219"/>
    <tag k="us.fo:kommununr" v="11"/>
  </node>
  (...)
  <node id="32946858" version="10" timestamp="2019-10-04T23:26:21Z" lat="62.0119587" lon="-6.7708066">
    <tag k="highway" v="traffic_signals"/>
  </node>
  (...)
  <node id="604981485" version="3" timestamp="2019-06-13T16:06:10Z" lat="62.0482742" lon="-7.1932612">
    <tag k="bus" v="yes"/>
    <tag k="highway" v="bus_stop"/>
    <tag k="public_transport" v="platform"/>
  </node>
  (...)
  <node id="1042145823" version="4" timestamp="2020-12-21T17:09:37Z" lat="61.5436929" lon="-6.7744527">
    <tag k="aeroway" v="helipad"/>
    <tag k="name" v="Frooba Heliport"/>
    <tag k="source" v="ourairports.com"/>
  </node>
  (...)
  <way id="38855555" version="3" timestamp="2022-03-19T23:29:17Z">
    <nd ref="461496369"/>
    <nd ref="461496370"/>
    <nd ref="9591003192"/>
    <nd ref="9591003191"/>
    <nd ref="461496371"/>
    <nd ref="461496372"/>
    <nd ref="9591003196"/>
    <nd ref="9591003195"/>
    <nd ref="9591003194"/>
    <nd ref="9591003193"/>
    <nd ref="461496369"/>
    <tag k="amenity" v="place_of_worship"/>
    <tag k="building" v="church"/>
    <tag k="name" v="Svínoyar kirkja"/>
    <tag k="religion" v="christian"/>
    <tag k="wikidata" v="Q104804403"/>
    <tag k="wikimedia_commons" v="Category:Svínoyar kirkja"/>
  </way>
  (...)
```
