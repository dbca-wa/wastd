<script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>
<script type="text/javascript">
  window.addEventListener("map:init", function (event) {
    var map = event.detail.map;
    {% include 'shared/overlays.html' %}
    map.addControl(new L.Control.Fullscreen());
    map.addControl(new L.Control.Geocoder());
});
</script>