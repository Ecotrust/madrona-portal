mapEngine = {};

mapEngine.updateSize = function() {
  app.map.updateSize();
};

mapEngine.setView = function(center, zoom, callback) {
  setTimeout(function() {
    if (app.wrapper.map.hasOwnProperty('animateView')) {
      app.wrapper.map.animateView(center, zoom, 1200);
    } else {
      app.wrapper.map.setCenter(center[0], center[1]);
      app.wrapper.map.setZoom(zoom);
    }

  }, 500);
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
      center: _.map(data.view.center, parseFloat),
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
    if (layer) {
      app.wrapper.map.setBasemap(layer);
      currentBaseLayer = layer;
    }

  }

  function fetchDataLayer(id) {
    if (!dataLayers.hasOwnProperty(id)) {
      if (!layerCatalog.hasOwnProperty(id)) {
        console.warn("Ignoring unknown layer id " + id);
        return false;
      }
      // create new layer, add to map, hide it, add to dataLayers at [ID]
      var layerObj = app.addLayerToMap(layerCatalog[id]);
      if (layerObj.hasOwnProperty('layer')) {
        layerObj = layerObj.layer;
      }
      dataLayers[id] = layerObj;
    }
    return dataLayers[id];
  }


  function setDataLayers(layers, hashLayerOverrides) {
    var layerKeys = Object.keys(layers);
    var overrideKeys = Object.keys(hashLayerOverrides);

    for (var i = 0; i < layerKeys.length; i++) {
      if (overrideKeys.indexOf(layerKeys[i]) >= 0) {
        var layer = layers[layerKeys[i]];
        var override = hashLayerOverrides[layerKeys[i]];
        var l = fetchDataLayer(layer.id);
        l.setOpacity(override.opacity);
        if (!l.hasOwnProperty('state_') || !l.state_) {
          l.state_ = {};
        }
        l.state_.zIndex = override.order;
        l.state_.opacity = override.opacity;
        l.state_.visible = override.display;
        if (!l.state_.hasOwnProperty('layer')) {
          l.state_.layer = l;
        }
      }
    }
    app.wrapper.map.sortLayers();

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

  function parseHash(url) {
    var hashObject = {};
    var hashParams = new URLSearchParams(url);
    var layerParams = hashParams.getAll('dls[]');
    var layerOrder = 0;
    while(layerParams.length > 2) {
      // RDH: this handles a case where both layer id and opacity are 1
      var newHashLayer = {'id':1, 'opacity':1, 'order': layerOrder};
      for (var i = 0; i < 3; i++) {
        if ([true, "True", 'true'].indexOf(layerParams[i])>= 0 ) {
          newHashLayer.display = true;
        } else if ( layerParams[i] >= newHashLayer.id && layerParams[i].toString().indexOf('.') < 0) {
          newHashLayer.id = parseInt(layerParams[i]);
        } else if (parseFloat(layerParams[i]) <= 1) {
          newHashLayer.opacity = parseFloat(layerParams[i]);
        }
      }
      if (newHashLayer.hasOwnProperty('display') && newHashLayer.display) {
        hashObject[newHashLayer.id.toString()] = newHashLayer;
      }
      layerParams = layerParams.slice(3);
      layerOrder ++;
    }
    return hashObject;
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
        setDataLayers(s.dataLayers, parseHash(s.url));
      });

    },
  };

};
