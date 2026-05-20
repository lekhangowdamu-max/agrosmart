// Utilities Routes (Map, Weather, Motor, Drone, CCTV)

const express = require('express');
const router = express.Router();
const { 
  getMapView, 
  getWeather, 
  getMotorStatus, 
  controlMotor,
  getDroneTelemetry, 
  updateDroneTelemetry, 
  getDroneLogs, 
  addDroneLog,
  getCCTVStatus 
} = require('../controllers/utilitiesController');
const { optionalUser } = require('../middleware/auth');

// Map routes
router.get('/map', optionalUser, getMapView);

// Weather routes
router.get('/weather', getWeather);

// Motor control routes (IoT endpoints)
router.get('/motor', getMotorStatus);
router.post('/motor/control', controlMotor);

// Drone routes
router.get('/drone/telemetry', getDroneTelemetry);
router.post('/drone/telemetry', updateDroneTelemetry);
router.get('/drone/logs', getDroneLogs);
router.post('/drone/logs', addDroneLog);

// CCTV routes
router.get('/cctv', getCCTVStatus);

module.exports = router;
