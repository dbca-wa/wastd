<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-tilelayer-geojson/1.0.4/TileLayer.GeoJSON.min.js"
  integrity="sha256-wAPWjo+rSGf0uCc0Bx0INODQ6En5mOPxSDGwKBLkfhg=" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.4.1/leaflet.markercluster.js"
  integrity="sha256-WL6HHfYfbFEkZOFdsJQeY7lJG/E5airjvqbznghUzRw=" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.5/Control.FullScreen.min.js"
  integrity="sha256-ymsQ8vmYkMvP0tBKzewWBBnPnYm308ZoRQpeStgVR2Y=" crossorigin="anonymous"></script>
<script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>
<script type="text/javascript">
  window.addEventListener("map:init", function (event) {
    var map = event.detail.map;
    {% include 'shared/overlays.html' %}
    map.addControl(new L.Control.Fullscreen());
    map.addControl(new L.Control.Geocoder());
});
</script>