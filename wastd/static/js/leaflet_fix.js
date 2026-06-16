(function () {
  function fixLeafletIcons() {
    if (!window.L || !L.Icon || !L.Icon.Default) {
      return;
    }

    // Prevent Leaflet from trying to auto-detect
    delete L.Icon.Default.prototype._getIconUrl;

    // Use globally available Django static URL
    const staticBase = window.STATIC_URL || '/static/';

    // Set leaflet icon URLs, rather than relying on L.Icon.Default.getIconUrl
    // whitenoise compression seems to break this.
    L.Icon.Default.mergeOptions({
      iconUrl: staticBase + 'leaflet/images/marker-icon.png',
      iconRetinaUrl: staticBase + 'leaflet/images/marker-icon-2x.png',
      shadowUrl: staticBase + 'leaflet/images/marker-shadow.png',
    });
  }

  // Run after load
  if (document.readyState === 'complete') {
    fixLeafletIcons();
  } else {
    window.addEventListener('load', fixLeafletIcons);
  }
})();
