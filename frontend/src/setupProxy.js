const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    ['/items', '/uploads', '/generate-outfit', '/outfits'],
    createProxyMiddleware({ target: 'http://localhost:8000', changeOrigin: true })
  );
};
