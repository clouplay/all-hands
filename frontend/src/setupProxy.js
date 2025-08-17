const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Allow all hosts
  app.use(function(req, res, next) {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
  });
};