// Map and Utilities Controller

const pool = require('../config/database');
const { getLocationCoordinates } = require('../utilities/helpers');

// Get map view with user location
const getMapView = async (req, res, next) => {
  try {
    let userLocation = 'Not set';
    let userCoords = null;

    if (req.session && req.session.userId) {
      const [users] = await pool.query(
        'SELECT location FROM users WHERE id = ?',
        [req.session.userId]
      );

      if (users.length > 0 && users[0].location) {
        userLocation = users[0].location;
        userCoords = getLocationCoordinates(userLocation);
      }
    }

    res.json({
      user_location: userLocation,
      user_coords: userCoords,
    });
  } catch (error) {
    next(error);
  }
};

// Get weather information
const getWeather = async (req, res, next) => {
  try {
    // Weather service is temporarily disabled
    res.json({
      weather: {
        error: 'Weather service temporarily disabled',
      },
    });
  } catch (error) {
    next(error);
  }
};

// Motor control dashboard data
const getMotorStatus = async (req, res, next) => {
  try {
    // IoT motor control status endpoint
    // This would connect to ESP8266 or other IoT devices
    res.json({
      motor: {
        status: 'offline',
        power: 0,
        flow: 0,
        pressure: 0,
      },
    });
  } catch (error) {
    next(error);
  }
};

// Control motor (IoT endpoint for ESP8266)
const controlMotor = async (req, res, next) => {
  try {
    const { action, power } = req.body;

    // Validate action
    if (!['on', 'off', 'set_power'].includes(action)) {
      return res.status(400).json({ error: 'Invalid action' });
    }

    // This would send command to IoT device
    const response = {
      status: 'success',
      action: action,
      timestamp: new Date().toISOString(),
    };

    if (action === 'set_power' && power) {
      response.power = power;
    }

    res.json(response);
  } catch (error) {
    next(error);
  }
};

// Drone telemetry
const getDroneTelemetry = async (req, res, next) => {
  try {
    const [telemetry] = await pool.query(
      `SELECT * FROM drone_telemetry 
       WHERE drone_id = 'agro-drone-001'
       ORDER BY created_at DESC LIMIT 1`
    );

    if (telemetry.length === 0) {
      return res.json({
        telemetry: {
          status: 'offline',
          battery: 0,
          altitude: 0,
          speed: 0,
          latitude: 0,
          longitude: 0,
        },
      });
    }

    res.json({
      telemetry: telemetry[0],
    });
  } catch (error) {
    next(error);
  }
};

// Update drone telemetry (IoT endpoint for Drone)
const updateDroneTelemetry = async (req, res, next) => {
  try {
    const { drone_id, status, battery, altitude, speed, latitude, longitude, heading, signal, mode, last_command, waypoint_latitude, waypoint_longitude } = req.body;

    const [result] = await pool.query(
      `INSERT INTO drone_telemetry 
       (drone_id, status, battery, altitude, speed, latitude, longitude, heading, signal, mode, last_command, waypoint_latitude, waypoint_longitude)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [drone_id || 'agro-drone-001', status, battery, altitude, speed, latitude, longitude, heading, signal, mode, last_command, waypoint_latitude, waypoint_longitude]
    );

    res.json({
      message: 'Telemetry updated successfully',
      telemetryId: result.insertId,
    });
  } catch (error) {
    next(error);
  }
};

// Get drone logs
const getDroneLogs = async (req, res, next) => {
  try {
    const limit = parseInt(req.query.limit) || 50;

    const [logs] = await pool.query(
      `SELECT * FROM drone_logs 
       WHERE drone_id = 'agro-drone-001'
       ORDER BY created_at DESC
       LIMIT ?`,
      [limit]
    );

    res.json({
      logs: logs,
    });
  } catch (error) {
    next(error);
  }
};

// Add drone log
const addDroneLog = async (req, res, next) => {
  try {
    const { drone_id, event, level } = req.body;

    if (!event) {
      return res.status(400).json({ error: 'Event is required' });
    }

    const [result] = await pool.query(
      `INSERT INTO drone_logs (drone_id, event, level)
       VALUES (?, ?, ?)`,
      [drone_id || 'agro-drone-001', event, level || 'info']
    );

    res.json({
      message: 'Log added successfully',
      logId: result.insertId,
    });
  } catch (error) {
    next(error);
  }
};

// CCTV stream status
const getCCTVStatus = async (req, res, next) => {
  try {
    res.json({
      cctv: {
        status: 'offline',
        cameras: [],
      },
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getMapView,
  getWeather,
  getMotorStatus,
  controlMotor,
  getDroneTelemetry,
  updateDroneTelemetry,
  getDroneLogs,
  addDroneLog,
  getCCTVStatus,
};
