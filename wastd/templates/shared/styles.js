/* Point style */
var pointstyle = {
    "clickable": true
};

/* Polygon style */
var polystyle = {
    "color": "#0009ff",
    "weight": 1,
    "opacity": 0.65
};

var polystyle_red = {
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
  //layer.bindPopup(feature.properties.label);
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
