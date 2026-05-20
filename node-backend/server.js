// Main Server File - server.js

require('dotenv').config();

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const session = require('express-session');
const path = require('path');
const fs = require('fs');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors({ origin: process.env.CORS_ORIGIN || '*' }));
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));

// Serve static files
const staticPath = path.join(__dirname, '../static');
if (fs.existsSync(staticPath)) {
  app.use('/static', express.static(staticPath));
}

// Session configuration
app.use(session({
  secret: process.env.SESSION_SECRET || 'your-secret-key',
  resave: false,
  saveUninitialized: true,
  cookie: {
    secure: process.env.SESSION_COOKIE_SECURE === 'true',
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
  },
}));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API Routes
const authRoutes = require('./routes/auth');
const machineryRoutes = require('./routes/machinery');
const bookingsRoutes = require('./routes/bookings');
const adminRoutes = require('./routes/admin');
const pricesRoutes = require('./routes/prices');
const utilitiesRoutes = require('./routes/utilities');

app.use('/api/auth', authRoutes);
app.use('/api/machinery', machineryRoutes);
app.use('/api/bookings', bookingsRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/prices', pricesRoutes);
app.use('/api', utilitiesRoutes);

// Legacy route support - redirect to API endpoints
// This allows the frontend to call both /login and /api/auth/login
app.post('/login', (req, res, next) => {
  req.url = '/api/auth/login';
  next();
});

app.post('/register', (req, res, next) => {
  req.url = '/api/auth/register';
  next();
});

app.post('/logout', (req, res, next) => {
  req.url = '/api/auth/logout';
  next();
});

// Use auth routes for legacy paths
app.use(authRoutes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    path: req.path,
  });
});

// Error handling middleware
const { errorHandler } = require('./middleware/errorHandler');
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║     AgroSmart Backend Server Started Successfully       ║
║                                                          ║
║  Server URL: http://localhost:${PORT}                         
║  Environment: ${process.env.NODE_ENV || 'development'}
║  Database: ${process.env.DB_HOST || 'localhost'}:${process.env.DB_PORT || 3306}/${process.env.DB_NAME || 'agrosmart'}
║                                                          ║
╚══════════════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\nServer shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n\nServer shutting down gracefully...');
  process.exit(0);
});

module.exports = app;
