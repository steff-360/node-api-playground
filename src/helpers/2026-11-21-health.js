// Endpoint de health check con info del sistema
const os = require('os');

function healthHandler(req, res) {
  const uptime = process.uptime();
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: `${Math.floor(uptime / 60)}m ${Math.floor(uptime % 60)}s`,
    memory: {
      used: `${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`,
      total: `${Math.round(os.totalmem() / 1024 / 1024)}MB`,
    },
    node: process.version,
    env: process.env.NODE_ENV || 'development',
  });
}
module.exports = healthHandler;
