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
  layer.setInvisible();
};

mapEngine.showLayer = function(layer) {
  layer.setVisible();
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
    if (!(dataLayers[id] instanceof layerModel)) {
      dataLayers[id] = app.viewModel.getLayerById(id);
    }
    return dataLayers[id];
  }

  app.wrapper.map.sortLayers = function() {
    // re-ordering map layers by z value
    app.map.layers = app.wrapper.map.getLayers();
    app.map.layers.sort(function(a, b) {
        // ascending sort
        if (a.getZIndex()!=undefined && b.getZIndex()!=undefined) {
          return a.getZIndex() - b.getZIndex();
        } else if (a.hasOwnProperty('state_') && a.state_){
          if (b.hasOwnProperty('state_') && b.state_) {
            return a.state_.zIndex - b.state_.zIndex;
          }
          return true;
        }
    });
  }


  function setDataLayers(layers, layerKeys, hashLayerOverrides) {
    var overrideKeys = Object.keys(hashLayerOverrides);

    // Hide layers from old state
    for (var i = 0; i < visibleDataLayers.length; i++) {
      if (layerKeys.indexOf(visibleDataLayers[i]) < 0) {
        var old_layer = app.viewModel.getLayerById(visibleDataLayers[i]);
        if (old_layer instanceof layerModel) {
          old_layer.setInvisible();
        }
      }
    }

    function loadStoryLayers() {
      for (var i = 0; i < layerKeys.length; i++) {
        var loadingLayer = app.viewModel.getLayerById(layerKeys[i]);
        loadingLayer.setVisible();
        dataLayers[layerKeys[i]] = loadingLayer;
        var l = fetchDataLayer(layerKeys[i]);
        if (!l.hasOwnProperty('state_') || !l.state_) {
          l.state_ = {};
        }
        if (overrideKeys.indexOf(layerKeys[i]) >= 0) {
          var override = hashLayerOverrides[layerKeys[i]];
          l.opacity(override.opacity);
          l.state_.zIndex = override.order;
          l.state_.opacity = override.opacity;
          l.state_.visible = override.display;
        }
        if (!l.state_.hasOwnProperty('layer')) {
          l.state_.layer = l;
        }
        l.layer.setZIndex(layerKeys.length - layerKeys.indexOf(l.id.toString()));
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

    function confirmAllLayersLoaded() {
      for (var i = 0; i < layerKeys.length; i++) {
        var pendingLayer = app.viewModel.getLayerById(layerKeys[i]);
        if (!pendingLayer.fullyLoaded) {
          return false;
        }
      }
      loadStoryLayers();
    }

    // Add layers from new state
    for (var i = 0; i < layerKeys.length; i++) {
        var layer = layers[layerKeys[i]];
        // RDH 20191119 - this is not a layermodel, but on object: enforce this and use timeout to watch for fullyloaded
        var loopTime = 0;
        function layerTestLoop () {
          setTimeout(function() {
            var mapLayer = app.viewModel.getLayerById(layer.id);
            if (!(mapLayer instanceof layerModel && mapLayer.fullyLoaded) && loopTime < 100) {
              loopTime ++;
              layerTestLoop();
            } else {
              confirmAllLayersLoaded();
            }
          }, 100);
        };
        fetchDataLayer(layerKeys[i]);
        layerTestLoop();
    }

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
        setDataLayers(s.dataLayers, s.layerOrder, parseHash(s.url));
      });

    },
  };

};
