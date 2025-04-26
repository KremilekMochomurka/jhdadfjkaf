const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const config = require('./config');
const searchRoutes = require('./routes/search');

// Initialize Express app
const app = express();

// Apply middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS for all routes
app.use(express.json()); // Parse JSON request bodies

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', message: 'MCP server is running' });
});

// Apply routes
app.use('/api', searchRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    error: true,
    message: 'Internal server error',
    details: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: true, message: 'Endpoint not found' });
});

// Start the server
const PORT = config.port;
app.listen(PORT, () => {
  console.log(`MCP server running on port ${PORT}`);
  console.log(`Health check available at http://localhost:${PORT}/health`);
  console.log(`API endpoints available at http://localhost:${PORT}/api/search`);
});
