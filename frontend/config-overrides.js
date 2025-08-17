module.exports = function override(config, env) {
  if (env === 'development') {
    config.devServer = {
      ...config.devServer,
      allowedHosts: 'all',
      host: '0.0.0.0',
      port: 12001,
    };
  }
  return config;
};