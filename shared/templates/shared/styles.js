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
function getIcon(feature){
    if (feature.properties.leaflet_icon){
        return feature.properties.leaflet_icon
    } else {
        return "eye"
    }
}

/* Map a feature to an marker colour */
function getMarkerColor(feature){
    if (feature.properties.leaflet_colour){
        return feature.properties.leaflet_colour
    } else {
        return "red"
    }
}

/* Use FontAwesome icons for Leafet.awesome-markers */
L.AwesomeMarkers.Icon.prototype.options.prefix = 'fa';

/* Return a grouping variable - using feature.id disables grouping */
function getUnique(feature){return feature.id}

/* Override default Marker, set colour, symbol; add mouse hover title */
function ptl(feature, latlng) {
    /* https://github.com/lvoogdt/Leaflet.awesome-markers */
    var icon = new L.AwesomeMarkers.icon({
        icon: getIcon(feature),
        iconColor: "white",
        markerColor: getMarkerColor(feature)
        // prefix: 'fa',
        // spin:false
    });

    return L.marker(latlng, {icon: icon});
    //title: feature.properties.leaflet_title,
}

/* Actions taken on each feature: title, popup, info preview */
function oef (feature, layer) {
    layer.bindTooltip(feature.properties.leaflet_title);
    layer.bindPopup(feature.properties.as_html);
    // layer.on({mouseover: highlightFeature, click: resetHighlight});
}

/* Actions taken on each feature: title, popup, info preview */
function oef_eoo (feature, layer) {
    layer.bindTooltip("Extent of Occurrence");
    // layer.bindPopup("Extent of Occurrence");
}

/* Actions taken on each feature: title, popup, info preview */
function oef_rel (feature, layer) {
  layer.bindTooltip('<strong><span class="oi oi-calendar" aria-hidden="true">' +
    feature.properties.encountered_on + '</strong><br/>');
  layer.bindPopup(feature.properties.as_html);
}

/* Override default Marker, set colour, symbol; add mouse hover title */
function ptlBioSys(feature, latlng) {
    /* https://github.com/lvoogdt/Leaflet.awesome-markers */
    var icon = new L.AwesomeMarkers.icon({icon: 'database', markerColor: 'green'});
    return L.marker(latlng, {icon: icon});
}

function oefBioSys(feature, layer) {
  layer.bindPopup(
    '<div class="row"><div class="mr-auto p-2"><h5>'+ feature.properties.species_name + '</h5></div></div>' +
    '<p><i class="oi oi-calendar" aria-hidden="true"></i> ' + feature.properties.datetime + '</p>' +
    '<p><a class="btn btn-secondary btn-sm" target="_" ' +
    'href="https://biosys-uat.dbca.wa.gov.au/#/data/projects/61/datasets/' +
    feature.properties.dataset + '/record/' + feature.id + '">' +
    '<i class="oi oi-pencil"></i> Edit this record in BioSys</a></p>'
  );
  layer.bindTooltip(
    'BioSys <br/><span class="oi oi-calendar" aria-hidden="true">' +
    feature.properties.datetime
  );
}

/* Turn a BioSys API record into a GeoJSON Feature. */
function geoJSONify(json_record) {
  return {
    type: 'Feature',
    id: json_record.id,
    geometry: {type: 'Point', coordinates: json_record.geometry.coordinates},
    properties: json_record
  };
}

function geoJSONfc(gj_feature_array) {
  return {"type": "FeatureCollection", "features": gj_feature_array.map(geoJSONify)}
}

/* Authentication headers for BioSys API. */
var hdr = new Headers();
hdr.append("Authorization", 'Basic ' + btoa('{{ settings.BIOSYS_UN }}:{{ settings.BIOSYS_PW }}'));