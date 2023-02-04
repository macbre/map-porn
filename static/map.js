// get a custom icon
// https://www.geoapify.com/create-custom-map-marker-icon
function getIcon(color /* green | blue | yellow */) {
    let size = 16;
    if (color === 'green') size = 24;

    // https://leafletjs.com/reference.html#divicon
    return L.divIcon({
        className: 'marker-icon',
        html: `<span class="marker ${color}">`,
        iconSize: [size, size],
        // The coordinates of the "tip" of the icon (relative to its top left corner).
        // The icon will be aligned so that this point is at the marker's geographical location.
        // Centered by default if size is specified, also can be set in CSS with negative margins.
        iconAnchor: [size >> 1, size >> 1],
    });
}

function setupMap(wrapperId, options, center, zoom) {
    const map = L.map(wrapperId, options).setView(center, zoom);
    // L.marker([lat, lon]).addTo(map);

    // https://leaflet-extras.github.io/leaflet-providers/preview/
    const ESRI = L.tileLayer.provider('Esri.WorldGrayCanvas')

    const CartoDB_VoyagerNoLabels = L.tileLayer.provider('CartoDB.VoyagerNoLabels');

    const Stamen_TonerLite = L.tileLayer.provider('Stamen.TonerLite');
    const Stamen_Watercolor = L.tileLayer.provider('Stamen.Watercolor');

    Stamen_Watercolor.addTo(map); // first background
    Stamen_Watercolor._level.el.id = 'watercolor';

    // Stamen_TonerLite.addTo(map); // then foreground
    // Stamen_TonerLite._level.el.id = 'toner-lite';

    // CartoDB_VoyagerNoLabels.addTo(map);
    // CartoDB_VoyagerNoLabels._level.el.id = 'cartodb';

    // ESRI.addTo(map);

    // L.marker([61.961667, -6.9675], {icon: getIcon('green')}).addTo(map);
    // L.marker([61.961667, -6.8675], {icon: getIcon('blue')}).addTo(map);
    // L.marker([61.951667, -6.9975], {icon: getIcon('yellow')}).addTo(map);

    return map;
}

// now load the GeoJSON data
// https://leafletjs.com/examples/geojson/
async function addGeoJSONLayer(map, url, color, label) {
    const res = await fetch(url);
    const geojsonFeatures = JSON.parse(await res.text());
    // console.log('GeoJSON', geojsonFeatures);
    L.geoJSON(geojsonFeatures, {
        onEachFeature: (feature, _layer) => {
            const geo = feature.geometry.coordinates;
            L.marker([geo[1], geo[0]], {icon: getIcon(color)}).addTo(map);
        }
    });

    console.log(`Added GeoJSON layer: ${geojsonFeatures.features.length} nodes, color ${color}, from ${url}`);

    // add a label
    const legendEntry = document.createElement('li');
    legendEntry.innerHTML = `<span class="marker ${color}"></span>${label}<span class="tally">${geojsonFeatures.features.length}</span>`;

    document.querySelector('legend ul').appendChild(legendEntry);
}
