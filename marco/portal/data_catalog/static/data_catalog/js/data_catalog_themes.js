window.addEventListener('load', function () {
  if (window.location.hash.length > 1) {
    setTimeout(function() {
      $(window.location.hash).next().children('div').children('h4').children('a').click();
    }, 500);
  }

});

loadedLayers = {};

getCatalogEntry = function(layerId){
  var layerKey = layerId.toString();
  if (Object.keys(loadedLayers).indexOf(layerKey) < 0) {
    $.ajax({
      url: '/data_manager/get_layer_catalog_content/' + layerKey,
      success: function(data) {
        $("#collapse-layer-" + layerKey).html(data.html);
        loadedLayers[layerKey] = 'Loaded';
      },
      error: function(data) {
        $("#collapse-layer-" + layerKey).html('<div class="layer-loading-panel">Failed to retrieve layer info.</div>');
        loadedLayers[layerKey] = 'Failed to load';
      }
    });
  }
  return true;
}
