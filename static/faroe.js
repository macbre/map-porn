const MAP_CENTER = [61.951667, -6.9675]; // west of Tórshavn

async function initMap( callback ) {
    const zoom = 10;
    const options = {
        zoomControl: false,
        attributionControl: false,
    };

    const map = setupMap('map', options, MAP_CENTER, zoom);

    // render a small map showing the location of our main map
    // https://leafletjs.com/reference.html#map-getbounds
    const smallMap = setupMap('small-map', options, [58, 0], 3);

    const mapBounds = map.getBounds();
    const bounds = [mapBounds.getNorthWest(), mapBounds.getSouthEast()];

    console.log('Map bounds', mapBounds, bounds);
    L.rectangle(bounds, {color: '#9f4342', weight: 1}).addTo(smallMap);

    // https://leaflet-extras.github.io/leaflet-providers/preview/
    //L.tileLayer.provider('Stamen.TerrainBackground').addTo(smallMap);

    // https://leaflet-extras.github.io/leaflet-providers/preview/#filter=Stamen.Watercolor
    // migrate to:
    // https://watercolormaps.collection.cooperhewitt.org/tile/watercolor/12/1205/1539.jpg
    // @see https://maps.stamen.com/stadia-partnership/
    L.tileLayer('https://watercolormaps.collection.cooperhewitt.org/tile/watercolor/{z}/{x}/{y}.jpg').addTo(smallMap);

    // paper-like background
    // map.createPane('paper');

    // add a countour of the Faroe Islands
    const countourData = await fetchGeoJSON('/geojson/us-lendiskort-us_lendiskort-15-oyggjar.json');
    const styleOptions = {
        // https://leafletjs.com/reference.html#path-option
        stroke: true,
        color: "transparent",   // stroke
        fillColor: "#f2efe9", // fill
        fillOpacity: 1,
        weight: 3,
        opacity: 1,
        interactive: false,
    };

    // https://leafletjs.com/examples/map-panes/
    map.createPane('countour');
    map.createPane('countour-fg'); map.getPane('countour-fg').style.zIndex = 450;

    // labels with Tórshavn and Klaksvik
    // https://leafletjs.com/reference.html#tooltip
    map.createPane('labels');
    map.getPane('labels').style.zIndex = 500;

    // L.tooltip({pane: 'labels'})
    //     .setLatLng( L.latLng(62.01028602180903, -6.7715189468887145) )
    //     .setContent('Tórshavn')
    //     .addTo(map);

    // L.tooltip({pane: 'labels', direction: 'right'})
    //     .setLatLng( L.latLng(62.22542530358552, -6.583687811563278) )
    //     .setContent('Klaksvík')
    //     .addTo(map);

    // https://leafletjs.com/examples/geojson/
    var geojson = L.geoJson(
        countourData,
        {
            style: {
                ...styleOptions,
                color: "#3c91d033",   // stroke
                weight: 25,
                fill: false,
            },
            // filter: function(feature, layer) {
             //    return true;
            // },
            pane: 'countour'
        }
    ).addTo(map);

    var geojson = L.geoJson(
        countourData,
        {
            style: {
                ...styleOptions,
                color: "#3c91d0ee",   // stroke
                weight: 3,
            },
            // filter: function(feature, layer) {
             //    return true;
            // },
            pane: 'countour-fg'
        }
    ).addTo(map);

    // https://leafletjs.com/reference.html#control-scale
    L.control.scale({
        metric: true,
        imperial: false,
        maxWidth: 350,
        position: 'bottomright',
    }).addTo(map);

    // https://github.com/turban/Leaflet.Graticule#example
    // Specify bold red lines instead of thin grey lines
    L.graticule({
        // https://leafletjs.com/reference.html#path
        style: {
            color: '#3c91d033',
            weight: 1
        },
        interval: 0.5
    }).addTo(map);

    // L.marker([61.961667, -6.9675], {icon: getIcon('green')}).addTo(map);

    // what's the size of the webpage?
    const wrapper = document.getElementById('wrapper');
    console.log('Page size: ', {
        width: wrapper.clientWidth + 50 /* margin x2 */ + 10 /* border x2 */,
        height: wrapper.clientHeight + 50 + 10,
    });

    if (typeof callback === 'function') {
        await callback(map);
    }
}