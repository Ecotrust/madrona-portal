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
  if (layer.fullyLoaded) {
    layer.setInvisible();
  } else {
    window.setTimeout(mapEngine.hideLayer, 100, layer);
  }
};

mapEngine.showLayer = function(layer) {
  if (layer.fullyLoaded) {
    layer.setVisible();
  } else {
    window.setTimeout(mapEngine.showLayer, 100, layer);
  }
};

mapEngine.parseHash = function(url) {
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

mapEngine.setBaseLayer = function(layer) {
  if (layer) {
    app.wrapper.map.setBasemap(layer);
  }
}

mapEngine.fetchDataLayer = function(id) {
  if (!mapEngine.dataLayers.hasOwnProperty(id)) {
    if (!mapEngine.layerCatalog.hasOwnProperty(id)) {
      // fake it - the layer is loaded by `app.addLayerToMap` and will query for the layer details from the ID alone.
      mapEngine.layerCatalog[id] = {'id': id, 'name': 'Loading...'};
    }
    // create new layer, add to map, hide it, add to dataLayers at [ID]
    var layerObj = app.addLayerToMap(mapEngine.layerCatalog[id]);
    if (layerObj.hasOwnProperty('layer')) {
      layerObj = layerObj.layer;
    }
    mapEngine.dataLayers[id] = layerObj;
  }
  if (!(mapEngine.dataLayers[id] instanceof layerModel)) {
    mapEngine.dataLayers[id] = app.viewModel.getLayerById(id);
  }
  return mapEngine.dataLayers[id];
}

mapEngine.dataLayers = {};

mapEngine.setDataLayers = function(layers, layerKeys, hashLayerOverrides) {
  var overrideKeys = Object.keys(hashLayerOverrides);

  var visibleDataLayers = [];
  var liveLayers = app.wrapper.map.getLayers();
  for (var i = 0; i < liveLayers.length; i++) {
    var vizLayer = liveLayers[i];
    var vizLayerId = vizLayer.get('mpid');
    if (vizLayerId) {
      visibleDataLayers.push(vizLayerId);
    }
  }

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
      mapEngine.dataLayers[layerKeys[i]] = loadingLayer;
      var l = mapEngine.fetchDataLayer(layerKeys[i]);
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

    mapEngine.cleanStateLayers(visibleDataLayers, layerKeys);

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
      mapEngine.fetchDataLayer(layerKeys[i]);
      layerTestLoop();
  }

}

mapEngine.cleanStateLayers = function(layerKeys) {
  var visibleDataLayers = [];
  var liveLayers = app.wrapper.map.getLayers();
  for (var i = 0; i < liveLayers.length; i++) {
    var vizLayer = liveLayers[i];
    var vizLayerId = vizLayer.get('mpid');
    if (vizLayerId) {
      visibleDataLayers.push(vizLayerId);
    }
  }


  var oldIds = _.difference(visibleDataLayers, layerKeys);
  _.each(oldIds, function(id) {
    l = mapEngine.fetchDataLayer(id);
    if (l){
      mapEngine.hideLayer(l);
    }
  });

  // add new layers
  var newIds = _.difference(layerKeys, visibleDataLayers);
  _.each(newIds, function(id) {
    l = mapEngine.fetchDataLayer(id);
    if (l){
      mapEngine.showLayer(l);
    }
  });
}

mapEngine.delayStateLoop = function(section_id, s, counter) {
  mapEngine.enforceState(section_id, s, counter);
}

mapEngine.enforceState = function(section_id, s, counter) {
  if (section_id == app.storySection && counter < 10) {
    mapEngine.cleanStateLayers(s.layerOrder)
    window.setTimeout(mapEngine.delayStateLoop, 1000, section_id, s, counter+1);
    
  }
}
  

mapEngine.updateMap = function(story, layerCatalog) {

  mapEngine.layerCatalog = layerCatalog;

  function normalizeSection(data) {
    data.view = {
      center: _.map(data.view.center, parseFloat),
      zoom: parseInt(data.view.zoom),
    };
  }
  story.sections.forEach(normalizeSection);  

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

  return {
    goToSection: function(section) {
      if (section > story.sections.length - 1) {
        console.warn("Requested story section " + (section+1) + ", but only " + story.sections.length + " are present.")
        return;
      }
      var s = story.sections[section];

      mapEngine.setView(s.view.center, s.view.zoom, function(){
        mapEngine.setBaseLayer(s.baseLayer);
        mapEngine.setDataLayers(s.dataLayers, s.layerOrder, mapEngine.parseHash(s.url));
      });

      window.setTimeout(mapEngine.delayStateLoop, 1000, section, s, 0);

    },
  };

};
