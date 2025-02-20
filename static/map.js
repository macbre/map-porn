// get a custom icon
// https://www.geoapify.com/create-custom-map-marker-icon
function getIcon(color /* green | blue | yellow */, label) {
    let size = 16;
    label = label ? ` title="${label}"`: '';

    // https://leafletjs.com/reference.html#divicon
    return L.divIcon({
        className: 'marker-icon',
        html: `<span class="marker ${color}"${label}>`,
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
    // const ESRI = L.tileLayer.provider('Esri.WorldGrayCanvas')

    // const CartoDB_VoyagerNoLabels = L.tileLayer.provider('CartoDB.VoyagerNoLabels');

    // const Stamen_TonerLite = L.tileLayer.provider('Stamen.TonerLite');
    // const Stamen_Watercolor = L.tileLayer.provider('Stamen.Watercolor');

    // Stamen_Watercolor.addTo(map); // first background
    // Stamen_Watercolor._level.el.id = 'watercolor';

    // Stamen_TonerLite.addTo(map); // then foreground
    // Stamen_TonerLite._level.el.id = 'toner-lite';

    // CartoDB_VoyagerNoLabels.addTo(map);
    // CartoDB_VoyagerNoLabels._level.el.id = 'cartodb';

    // ESRI.addTo(map);

    // L.marker([61.961667, -6.9675], {icon: getIcon('green')}).addTo(map);
    // L.marker([61.961667, -6.8675], {icon: getIcon('blue')}).addTo(map);
    // L.marker([61.951667, -6.9975], {icon: getIcon('yellow')}).addTo(map);

    // create color panes
    // https://leafletjs.com/examples/map-panes/
    ['blue', 'yellow', 'green', 'red', 'dark-green', 'orange', 'black'].forEach(color => {
        map.createPane(`markers-${color}`);
        map.getPane(`markers-${color}`).style.zIndex = {
            'blue': 600,
            'yellow': 700,
            'green': 800,
            'red': 900,
            'dark-green': 1000,
            'orange': 1000,
            'black': 1100,
        }[color] || 500;
    });

    return map;
}

// now load the GeoJSON data
// https://leafletjs.com/examples/geojson/
async function addGeoJSONLayer(map, url, color, label_en, label_pl, filter) {
    const geojsonFeatures = await fetchGeoJSON(url);
    let count = 0;

    // console.log('GeoJSON', geojsonFeatures);
    L.geoJSON(geojsonFeatures, {
        onEachFeature: (feature, _layer) => {
            if (typeof filter === 'function' && filter(feature) === false) {
                return;
            }

            const geo = feature.geometry.coordinates;
            L.marker([geo[1], geo[0]], {icon: getIcon(color), pane: `markers-${color}`}).addTo(map);

            count++;
        }
    });

    console.log(`Added GeoJSON layer: ${count} nodes, color ${color}, from ${url}`);

    addLabel(color, label_en, label_pl, count);
}

function addLabel(color, label_en, label_pl, count) {
    // add a label
    const legendEntry = document.createElement('li');
    legendEntry.innerHTML = `<span class="marker ${color}"></span>` + 
        `<span lang="en">${label_en}</span><span lang="pl">${label_pl}</span>` + 
        `<span class="tally">${count}</span>`;

    document.querySelector('legend ul').appendChild(legendEntry);
}

/**
 * @param {string} url 
 * @returns {string}
 */
async function fetchGeoJSON(url) {
    console.log(`Fetching GeoJSON from <${url}> ...`);

    const res = await fetch(url);
    return await res.json();
}
