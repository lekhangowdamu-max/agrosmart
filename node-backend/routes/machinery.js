// Machinery Routes

const express = require('express');
const router = express.Router();
const { getAllMachinery, getMachineryById, createMachinery, updateMachinery, deleteMachinery } = require('../controllers/machineryController');
const { requireAdmin } = require('../middleware/auth');

// GET /api/machinery
router.get('/', getAllMachinery);

// GET /api/machinery/:machineId
router.get('/:machineId', getMachineryById);

// POST /api/machinery (Admin only)
router.post('/', requireAdmin, createMachinery);

// PUT /api/machinery/:machineId (Admin only)
router.put('/:machineId', requireAdmin, updateMachinery);

// DELETE /api/machinery/:machineId (Admin only)
router.delete('/:machineId', requireAdmin, deleteMachinery);

module.exports = router;
