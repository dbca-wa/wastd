"use strict";
/* Point style */
const pointstyle = {
    "clickable": true
};

/* Polygon style */
const polystyle = {
    "color": "#0009ff",
    "weight": 1,
    "opacity": 0.65
};

const polystyle_red = {
    "color": "#ff2200",
    "weight": 1,
    "opacity": 0.65
};

/* Map a feature to an icon class */
function getIcon(feature) {
    if (feature.properties.leaflet_icon) {
        return feature.properties.leaflet_icon
    } else {
        return "eye"
    }
}

/* Map a feature to an marker colour */
function getMarkerColor(feature) {
    if (feature.properties.leaflet_colour) {
        return feature.properties.leaflet_colour
    } else {
        return "white"
    }
}

/* Use FontAwesome icons for Leafet.awesome-markers */
L.AwesomeMarkers.Icon.prototype.options.prefix = 'fa';

/* Return a grouping variable - using feature.id disables grouping */
function getUnique(feature) { return feature.id }

/* Override default Marker, set colour, symbol; add mouse hover title */
function ptl(feature, latlng) {
    /* https://github.com/lvoogdt/Leaflet.awesome-markers */
    var icon = new L.AwesomeMarkers.icon({
        icon: getIcon(feature),
        iconColor: "white",
        markerColor: getMarkerColor(feature)
    });

    return L.marker(latlng, { icon: icon });
}

function ptl_svs(feature, latlng) {
    /* https://github.com/lvoogdt/Leaflet.awesome-markers */
    var icon = new L.AwesomeMarkers.icon({
        icon: "fa-solid fa-play",
        //iconColor: "green",
        markerColor: "blue"
    });

    return L.marker(latlng, { icon: icon });
}

function ptl_sve(feature, latlng) {
    /* https://github.com/lvoogdt/Leaflet.awesome-markers */
    var icon = new L.AwesomeMarkers.icon({
        icon: "fa-solid fa-stop",
        //iconColor: "red",
        markerColor: "blue"
    });

    return L.marker(latlng, { icon: icon });
}

/* Actions taken on each feature: title, popup, info preview */
function oef(feature, layer) {
  layer.bindTooltip(feature.properties.leaflet_title);
}

function oef_wideTT(feature, layer) {
  layer.bindTooltip(feature.properties.label, {className: 'leaflet-tooltip-wide'});
  layer.bindPopup(feature.properties.label);
}

/* Actions taken on each feature: title, popup, info preview */
function oef_ll(feature, layer) {
  layer.bindTooltip(feature.properties.leaflet_title);
  layer.bindPopup(feature.properties.as_html);
}

function oef_llwideTT(feature, layer) {
  layer.bindTooltip(feature.properties.leaflet_title, {className: 'leaflet-tooltip-wide'});
  layer.bindPopup(feature.properties.as_html);
}

/* Actions taken on each feature: title, popup, info preview */
function oef_eoo(feature, layer) {
  layer.bindTooltip("Extent of Occurrence");
}

/* Actions taken on each feature: title, popup, info preview */
function oef_rel(feature, layer) {
  layer.bindTooltip(feature.properties.label);
  layer.bindPopup(feature.properties.as_html);
}

// NOTE: some global variables are set in the base template:
// mapproxy_url

// Define baselayer tile layers.
const aerialImagery = L.tileLayer.wms(mapproxy_url, {
  layers: 'mapbox-satellite',
  tileSize: 1024,
  zoomOffset: -2,
});
const mapboxStreets = L.tileLayer.wms(mapproxy_url, {
  layers: 'mapbox-streets',
  format: 'image/png',
  tileSize: 1024,
  zoomOffset: -2,
});
const waCoast = L.tileLayer.wms(mapproxy_url, {
  layers: 'wa-coast',
  format: 'image/png',
  tileSize: 1024,
  zoomOffset: -2,
});

// Define overlay tile layers.
const dbcaRegions = L.tileLayer.wms(mapproxy_url, {
  layers: 'dbca-regions',
  format: 'image/png',
  transparent: true,
  opacity: 0.75,
  tileSize: 1024,
  zoomOffset: -2,
});
const dbcaDistricts = L.tileLayer.wms(mapproxy_url, {
  layers: 'dbca-districts',
  format: 'image/png',
  transparent: true,
  opacity: 0.75,
  tileSize: 1024,
  zoomOffset: -2,
});
const dbcaTenure = L.tileLayer.wms(mapproxy_url, {
  layers: 'dbca-tenure',
  format: 'image/png',
  transparent: true,
  opacity: 0.75,
  tileSize: 1024,
  zoomOffset: -2,
});
const ucl = L.tileLayer.wms(mapproxy_url, {
  layers: 'ucl',
  format: 'image/png',
  transparent: true,
  opacity: 0.75,
  tileSize: 1024,
  zoomOffset: -2,
});
const ibra = L.tileLayer.wms(mapproxy_url, {
  layers: 'ibra7-aust',
  format: 'image/png',
  transparent: true,
  opacity: 0.75,
  tileSize: 1024,
  zoomOffset: -2,
});
const lgaBoundaries = L.tileLayer.wms(mapproxy_url, {
  layers: 'lga-boundaries',
  format: 'image/png',
  transparent: true,
  opacity: 0.75,
  tileSize: 1024,
  zoomOffset: -2,
});

// Define map.
var map = L.map('map', {
    crs: L.CRS.EPSG4326,
    center: [-31.96, 115.87],
    minZoom: 4,
    maxZoom: 18,
    layers: [aerialImagery],  // Sets default selections.
    attributionControl: false,
});

// Define layer groups.
var baseMaps = {
    "Aerial imagery": aerialImagery,
    "Place names": mapboxStreets,
    "WA coast": waCoast,
};
var overlayMaps = {
    "DBCA regions": dbcaRegions,
    "DBCA districts": dbcaDistricts,
    "DBCA tenure": dbcaTenure,
    "Unallocated Crown Land": ucl,
    "IBRA 7 boundaries": ibra,
    "LGA boundaries": lgaBoundaries,
};

// Define layer control.
L.control.layers(baseMaps, overlayMaps).addTo(map);

// Define scale bar
L.control.scale({maxWidth: 500, imperial: false}).addTo(map);

// Log zoom level to console.
//map.on('zoomend', function (e) {console.log(e.target._zoom)});

  // Add a fullscreen control to the map.
const fullScreen = new L.control.fullscreen();
map.addControl(fullScreen);
