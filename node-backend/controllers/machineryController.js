// Machinery Controller

const pool = require('../config/database');

// Get all machinery
const getAllMachinery = async (req, res, next) => {
  try {
    const [machines] = await pool.query(
      'SELECT id, name, location, price_per_day, owner_contact, image_url, tracking_location FROM machinery ORDER BY id ASC'
    );

    res.json({
      machines: machines || [],
    });
  } catch (error) {
    next(error);
  }
};

// Get machinery by ID
const getMachineryById = async (req, res, next) => {
  try {
    const { machineId } = req.params;

    const [machines] = await pool.query(
      'SELECT id, name, location, price_per_day, owner_contact, image_url, tracking_location FROM machinery WHERE id = ?',
      [machineId]
    );

    if (machines.length === 0) {
      return res.status(404).json({ error: 'Machinery not found' });
    }

    res.json({
      machine: machines[0],
    });
  } catch (error) {
    next(error);
  }
};

// Create machinery (Admin only)
const createMachinery = async (req, res, next) => {
  try {
    const { name, location, price_per_day, owner_contact, image_url } = req.body;

    if (!name || !location) {
      return res.status(400).json({ error: 'Name and location are required' });
    }

    const [result] = await pool.query(
      'INSERT INTO machinery (name, location, price_per_day, owner_contact, image_url) VALUES (?, ?, ?, ?, ?)',
      [name, location, price_per_day || null, owner_contact || null, image_url || null]
    );

    res.status(201).json({
      message: 'Machinery created successfully',
      machineId: result.insertId,
    });
  } catch (error) {
    next(error);
  }
};

// Update machinery (Admin only)
const updateMachinery = async (req, res, next) => {
  try {
    const { machineId } = req.params;
    const { name, location, price_per_day, owner_contact, image_url, tracking_location } = req.body;

    const [result] = await pool.query(
      'UPDATE machinery SET name = ?, location = ?, price_per_day = ?, owner_contact = ?, image_url = ?, tracking_location = ?, updated_at = NOW() WHERE id = ?',
      [name, location, price_per_day || null, owner_contact || null, image_url || null, tracking_location || null, machineId]
    );

    if (result.affectedRows === 0) {
      return res.status(404).json({ error: 'Machinery not found' });
    }

    res.json({
      message: 'Machinery updated successfully',
    });
  } catch (error) {
    next(error);
  }
};

// Delete machinery (Admin only)
const deleteMachinery = async (req, res, next) => {
  try {
    const { machineId } = req.params;

    const [result] = await pool.query(
      'DELETE FROM machinery WHERE id = ?',
      [machineId]
    );

    if (result.affectedRows === 0) {
      return res.status(404).json({ error: 'Machinery not found' });
    }

    res.json({
      message: 'Machinery deleted successfully',
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getAllMachinery,
  getMachineryById,
  createMachinery,
  updateMachinery,
  deleteMachinery,
};
