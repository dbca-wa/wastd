<script type="text/javascript">
/* Project specific Javascript goes here. */
/*
 * Workaround for 1px lines appearing in some browsers due to
 * fractional transforms and resulting anti-aliasing.
 * https://github.com/Leaflet/Leaflet/issues/3575
 */
(function(){
    // L.Icon.Default.imagePath = '/static/leaflet/images/';
    delete L.Icon.Default.prototype._getIconUrl
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: "/static/leaflet/images/marker-icon-2x.png",
      iconUrl: "/static/leaflet/images/marker-icon.png",
      shadowUrl: "/static/leaflet/images/marker-shadow.png"
    })

    var originalInitTile = L.GridLayer.prototype._initTile
    L.GridLayer.include({
        _initTile: function (tile) {
            originalInitTile.call(this, tile);
            var tileSize = this.getTileSize();
            tile.style.width = tileSize.x + 1 + 'px';
            tile.style.height = tileSize.y + 1 + 'px';
        }
    });
})()

  window.addEventListener("map:init", function (event) {
    var map = event.detail.map;
    {% include 'shared/styles.js' %}
    {% include 'shared/overlays.html' %}
    map.addControl(new L.control.fullscreen());
    map.addControl(new L.Control.Geocoder({placeholder: '⇧+⏎ to search'}));
});
</script>