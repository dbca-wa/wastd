<script type="text/javascript">
  window.addEventListener("map:init", function (event) {
    var map = event.detail.map;
    {% include 'shared/overlays.html' %}
    map.addControl(new L.Control.Fullscreen());
});
</script>