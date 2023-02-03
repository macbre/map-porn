function setupMap(wrapperId, options, center, zoom) {
    const map = L.map(wrapperId, options).setView(center, zoom);
    // L.marker([lat, lon]).addTo(map);

    // https://leaflet-extras.github.io/leaflet-providers/preview/
    const CartoDB_VoyagerNoLabels = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    });

    // https://docs.eegeo.com/eegeo.js/v0.1.280/docs/leaflet/L.TileLayer/
    var Stamen_TonerLite = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}{r}.{ext}', {
        attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        subdomains: 'abcd',
        minZoom: 0,
        maxZoom: 20,
        ext: 'png',
        detectRetina: true,
    });

    var Stamen_Watercolor = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}', {
        attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        subdomains: 'abcd',
        minZoom: 1,
        maxZoom: 16,
        ext: 'jpg',
        detectRetina: true,
    });

    Stamen_Watercolor.addTo(map); // first background
    Stamen_Watercolor._level.el.id = 'watercolor';

    // Stamen_TonerLite.addTo(map); // then foreground
    // Stamen_TonerLite._level.el.id = 'toner-lite';

    // CartoDB_VoyagerNoLabels.addTo(map);

    // a custom icon
    // https://www.geoapify.com/create-custom-map-marker-icon
    function getIcon(color /* green | blue | yellow */) {
        return L.divIcon({
            className: 'marker-icon',
            html: `<span class="marker ${color}">`,
            iconSize: [36, 36],
            // The coordinates of the "tip" of the icon (relative to its top left corner).
            // The icon will be aligned so that this point is at the marker's geographical location.
            // Centered by default if size is specified, also can be set in CSS with negative margins.
            iconAnchor: [18, 18],
        });
    }

    L.marker([61.961667, -6.9675], {icon: getIcon('green')}).addTo(map);
    L.marker([61.961667, -6.8675], {icon: getIcon('blue')}).addTo(map);
    L.marker([61.951667, -6.9975], {icon: getIcon('yellow')}).addTo(map);
}