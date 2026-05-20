// Prices Routes

const express = require('express');
const router = express.Router();
const { getCropPrices, getStates, getDistricts, getCommodities, getPriceHistory, addCropPrice } = require('../controllers/pricesController');
const { requireAdmin } = require('../middleware/auth');

// GET /api/prices
router.get('/', getCropPrices);

// GET /api/prices/states
router.get('/states', getStates);

// GET /api/prices/districts
router.get('/districts', getDistricts);

// GET /api/prices/commodities
router.get('/commodities', getCommodities);

// GET /api/prices/history
router.get('/history', getPriceHistory);

// POST /api/prices (Admin only)
router.post('/', requireAdmin, addCropPrice);

module.exports = router;
