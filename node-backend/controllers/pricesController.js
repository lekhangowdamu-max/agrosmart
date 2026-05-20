// Prices Controller

const pool = require('../config/database');
const { getKannadaName } = require('../utilities/helpers');

// Get crop prices with filters
const getCropPrices = async (req, res, next) => {
  try {
    const { state, district, commodity } = req.query;
    let query = 'SELECT * FROM crop_prices WHERE 1=1';
    const params = [];

    if (state) {
      query += ' AND state = ?';
      params.push(state);
    }

    if (district) {
      query += ' AND district = ?';
      params.push(district);
    }

    if (commodity) {
      query += ' AND commodity = ?';
      params.push(commodity);
    }

    query += ' ORDER BY arrival_date DESC LIMIT 50';

    const [prices] = await pool.query(query, params);

    // Add Kannada names
    const formattedPrices = prices.map(p => ({
      ...p,
      kannada_name: getKannadaName(p.commodity),
    }));

    res.json({
      prices: formattedPrices,
    });
  } catch (error) {
    next(error);
  }
};

// Get unique states
const getStates = async (req, res, next) => {
  try {
    const [states] = await pool.query(
      'SELECT DISTINCT state FROM crop_prices WHERE state IS NOT NULL ORDER BY state'
    );

    res.json({
      states: states.map(s => s.state),
    });
  } catch (error) {
    next(error);
  }
};

// Get unique districts for a state
const getDistricts = async (req, res, next) => {
  try {
    const { state } = req.query;

    if (!state) {
      return res.status(400).json({ error: 'State parameter is required' });
    }

    const [districts] = await pool.query(
      'SELECT DISTINCT district FROM crop_prices WHERE state = ? AND district IS NOT NULL ORDER BY district',
      [state]
    );

    res.json({
      districts: districts.map(d => d.district),
    });
  } catch (error) {
    next(error);
  }
};

// Get unique commodities for a district
const getCommodities = async (req, res, next) => {
  try {
    const { district } = req.query;

    if (!district) {
      return res.status(400).json({ error: 'District parameter is required' });
    }

    const [commodities] = await pool.query(
      'SELECT DISTINCT commodity FROM crop_prices WHERE district = ? AND commodity IS NOT NULL ORDER BY commodity',
      [district]
    );

    res.json({
      commodities: commodities.map(c => c.commodity),
    });
  } catch (error) {
    next(error);
  }
};

// Get price history for a commodity
const getPriceHistory = async (req, res, next) => {
  try {
    const { commodity, district } = req.query;

    if (!commodity || !district) {
      return res.status(400).json({ error: 'Commodity and district parameters are required' });
    }

    const [history] = await pool.query(
      `SELECT arrival_date, modal_price FROM crop_prices 
       WHERE commodity = ? AND district = ?
       ORDER BY arrival_date ASC LIMIT 30`,
      [commodity, district]
    );

    const priceHistory = {
      dates: history.map(h => new Date(h.arrival_date).toISOString().split('T')[0]),
      prices: history.map(h => h.modal_price),
    };

    res.json({
      priceHistory,
    });
  } catch (error) {
    next(error);
  }
};

// Add new crop price (Admin only)
const addCropPrice = async (req, res, next) => {
  try {
    if (!req.session || req.session.role !== 'admin') {
      return res.status(403).json({ error: 'Admin privileges required' });
    }

    const { state, district, market, commodity, variety, grade, arrival_date, min_price, max_price, modal_price } = req.body;

    const [result] = await pool.query(
      `INSERT INTO crop_prices 
       (state, district, market, commodity, variety, grade, arrival_date, min_price, max_price, modal_price) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [state, district, market, commodity, variety, grade, arrival_date, min_price, max_price, modal_price]
    );

    res.status(201).json({
      message: 'Crop price added successfully',
      priceId: result.insertId,
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getCropPrices,
  getStates,
  getDistricts,
  getCommodities,
  getPriceHistory,
  addCropPrice,
};
