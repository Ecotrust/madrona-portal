map = app.map;

mapEngine = {};
mapEngine.updateSize = function() {
  map.updateSize();
};

mapEngine.setView = function(center, zoom, callback) {
  app.wrapper.map.setCenter(center);
  app.wrapper.map.setZoom(zoom);
  callback();
}

mapEngine.typeCreateHandlers = {
  'ArcRest': app.wrapper.map.addArcRestLayerToMap,
  'Cadastre': app.wrapper.map.addWMSLayerToMap,
  'Vector': app.wrapper.map.addVectorLayerToMap,
  'VectorTile': app.wrapper.map.addVectorTileLayerToMap,
  'WMS': app.wrapper.map.addWMSLayerToMap,
  'XYZ': app.wrapper.map.addXYZLayerToMap,

};

mapEngine.hideLayer = function(layer) {
  layer.setVisible(false);
};

mapEngine.showLayer = function(layer) {
  layer.setVisible(true);
};

mapEngine.updateMap = function(story, layerCatalog) {

  function normalizeSection(data) {
    data.view = {
      // center: _.map(data.view.center, parseFloat),
      center: ol.proj.transform(data.view.center, "EPSG:4326", map.getView().getProjection().code_),
      zoom: parseInt(data.view.zoom),
    };
  }
  story.sections.forEach(normalizeSection);

  var dataLayers = {};
  var visibleDataLayers = [];
  var currentBaseLayer;

  function defaultBaseLayer() {
    // return first base layer
    for (k in app.wrapper.baseLayers) {
      return k.name;
    }
  }

  function setBaseLayer(layer) {
    app.setBasemap('layer');
    currentBaseLayer = layer;

  }

  function fetchDataLayer(id) {
    if (!dataLayers.hasOwnProperty(id)) {
      if (!layerCatalog.hasOwnProperty(id)) {
        console.warn("Ignoring unknown layer id " + id);
        return false;
      }
      // create new layer, add to map, hide it, add to dataLayers at [ID]
      var layerObj = mapEngine.typeCreateHandlers[layerCatalog[id].layer_type](layerCatalog[id]);
      mapEngine.hideLayer(layerObj);
      dataLayers[id] = layerObj;
    }
    return dataLayers[id];
  }

  function setDataLayers(layers) {
    var layerKeys = Object.keys(layers)

    // trim unused layers
    _.each(_.difference(visibleDataLayers, layerKeys), function(id) {
      l = fetchDataLayer(id);
      if (l){
        mapEngine.hideLayer(l);
      }
    });

    // add new layers
    _.each(_.difference(layerKeys, visibleDataLayers), function(id) {
      l = fetchDataLayer(id);
      if (l){
        mapEngine.showLayer(l);
      }
    });
    visibleDataLayers = layerKeys;
  }

  return {
    goToSection: function(section) {
      if (section > story.sections.length - 1) {
        console.warn("Requested story section " + (section+1) + ", but only " + story.sections.length + " are present.")
        return;
      }
      var s = story.sections[section];

      mapEngine.setView(s.view.center, s.view.zoom, function(){
        setBaseLayer(s.baseLayer);
        setDataLayers(s.dataLayers);
      });
    },
  };

};
