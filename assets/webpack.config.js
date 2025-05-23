//https://github.com/webpack/webpack/issues/503
var path = require('path');

var projectRoot = path.join(__dirname,'..','..');
var projectApps = [
  'marco_site',
  'portal/ocean_stories',
].map(function(app){ return path.join(projectRoot,app,'static')});

var roots = projectApps;
roots.push(__dirname);
roots.push(path.join(__dirname, "node_modules"));

module.exports = {
  entry: {
    ocean_story: path.join(__dirname,'..','/marco/portal/ocean_stories/static/portal/ocean_story/index.js'),
    marco_site: "javascript/marco_site.js",
  },
  output: {
    path: path.join(__dirname, '..', 'static', 'bundles'),
    filename: "[name].js",
    chunkFilename: "[id].js",
    // comment to minify
    // debug: true
  },
  resolve: {
    root: roots,
  },
  resolveLoader: {
    root: path.join(__dirname, "node_modules"),
  },
  externals: {
    'openlayers': 'var window.ol',
  },
};
