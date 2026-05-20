// Booking Controller

const pool = require('../config/database');
const { calculateBookingCost, formatDate } = require('../utilities/helpers');

// Create a booking
const createBooking = async (req, res, next) => {
  try {
    if (!req.session || !req.session.userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { machineId, startDate, endDate, notes } = req.body;
    const userId = req.session.userId;

    // Validation
    if (!machineId || !startDate || !endDate) {
      return res.status(400).json({ error: 'Machine ID, start date, and end date are required' });
    }

    // Get machine details
    const [machines] = await pool.query(
      'SELECT price_per_day FROM machinery WHERE id = ?',
      [machineId]
    );

    if (machines.length === 0) {
      return res.status(404).json({ error: 'Machinery not found' });
    }

    // Validate dates
    const start = new Date(startDate);
    const end = new Date(endDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (start >= end) {
      return res.status(400).json({ error: 'End date must be after start date' });
    }

    if (start < today) {
      return res.status(400).json({ error: 'Start date cannot be in the past' });
    }

    // Calculate total cost
    const totalCost = calculateBookingCost(startDate, endDate, machines[0].price_per_day);

    // Get user location
    const [users] = await pool.query(
      'SELECT location FROM users WHERE id = ?',
      [userId]
    );

    const farmerLocation = users[0]?.location || 'Not set';

    // Create booking
    const [result] = await pool.query(
      'INSERT INTO bookings (machine_id, user_id, start_date, end_date, total_cost, notes, farmer_location, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [machineId, userId, startDate, endDate, totalCost, notes || null, farmerLocation, 'pending']
    );

    res.status(201).json({
      message: 'Booking request submitted successfully',
      bookingId: result.insertId,
      totalCost: totalCost,
    });
  } catch (error) {
    next(error);
  }
};

// Get user's bookings
const getUserBookings = async (req, res, next) => {
  try {
    if (!req.session || !req.session.userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const userId = req.session.userId;

    const [bookings] = await pool.query(
      `SELECT 
        b.id, b.machine_id, b.start_date, b.end_date, b.total_cost, 
        b.status, b.created_at, b.notes, b.admin_phone, b.admin_vehicle_number, 
        b.admin_photo, b.admin_location,
        m.name as machine_name, m.image_url as machine_image, m.location as machine_location
      FROM bookings b
      JOIN machinery m ON b.machine_id = m.id
      WHERE b.user_id = ?
      ORDER BY b.created_at DESC`,
      [userId]
    );

    const formattedBookings = bookings.map(b => ({
      id: b.id,
      machine_name: b.machine_name,
      machine_image: b.machine_image,
      machine_location: b.machine_location,
      start_date: formatDate(b.start_date),
      end_date: formatDate(b.end_date),
      total_cost: b.total_cost || 0,
      status: b.status,
      created_at: b.created_at,
      notes: b.notes,
      admin_phone: b.admin_phone,
      admin_vehicle_number: b.admin_vehicle_number,
      admin_photo: b.admin_photo,
      admin_location: b.admin_location,
    }));

    res.json({
      bookings: formattedBookings,
    });
  } catch (error) {
    next(error);
  }
};

// Get booking by ID
const getBookingById = async (req, res, next) => {
  try {
    const { bookingId } = req.params;

    if (!req.session || !req.session.userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const [bookings] = await pool.query(
      `SELECT 
        b.*, m.name as machine_name, m.image_url as machine_image, m.location as machine_location,
        u.name as user_name, u.email as user_email, u.location as user_location
      FROM bookings b
      JOIN machinery m ON b.machine_id = m.id
      JOIN users u ON b.user_id = u.id
      WHERE b.id = ? AND b.user_id = ?`,
      [bookingId, req.session.userId]
    );

    if (bookings.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    const booking = bookings[0];
    res.json({
      booking: {
        id: booking.id,
        machine_name: booking.machine_name,
        machine_image: booking.machine_image,
        machine_location: booking.machine_location,
        user_name: booking.user_name,
        user_email: booking.user_email,
        user_location: booking.user_location,
        start_date: formatDate(booking.start_date),
        end_date: formatDate(booking.end_date),
        total_cost: booking.total_cost,
        status: booking.status,
        notes: booking.notes,
        admin_phone: booking.admin_phone,
        admin_vehicle_number: booking.admin_vehicle_number,
        admin_location: booking.admin_location,
      },
    });
  } catch (error) {
    next(error);
  }
};

// Cancel booking
const cancelBooking = async (req, res, next) => {
  try {
    if (!req.session || !req.session.userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { bookingId } = req.params;
    const userId = req.session.userId;

    // Get booking
    const [bookings] = await pool.query(
      'SELECT status FROM bookings WHERE id = ? AND user_id = ?',
      [bookingId, userId]
    );

    if (bookings.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    const booking = bookings[0];
    if (!['pending', 'approved'].includes(booking.status)) {
      return res.status(400).json({ error: 'Cannot cancel this booking' });
    }

    // Cancel booking
    await pool.query(
      'UPDATE bookings SET status = ?, updated_at = NOW() WHERE id = ?',
      ['cancelled', bookingId]
    );

    res.json({
      message: 'Booking cancelled successfully',
    });
  } catch (error) {
    next(error);
  }
};

// Get booking tracking info
const getBookingTracking = async (req, res, next) => {
  try {
    const { bookingId } = req.params;

    if (!req.session || !req.session.userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const [bookings] = await pool.query(
      `SELECT 
        b.*, m.name as machine_name, m.tracking_location, m.location as machine_location,
        u.location as user_location
      FROM bookings b
      JOIN machinery m ON b.machine_id = m.id
      JOIN users u ON b.user_id = u.id
      WHERE b.id = ? AND b.user_id = ?`,
      [bookingId, req.session.userId]
    );

    if (bookings.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    const booking = bookings[0];
    res.json({
      booking: {
        id: booking.id,
        machine_name: booking.machine_name,
        machine_location: booking.machine_location,
        admin_location: booking.admin_location,
        user_location: booking.user_location,
        admin_phone: booking.admin_phone,
        admin_vehicle_number: booking.admin_vehicle_number,
        start_date: formatDate(booking.start_date),
        end_date: formatDate(booking.end_date),
        status: booking.status,
      },
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  createBooking,
  getUserBookings,
  getBookingById,
  cancelBooking,
  getBookingTracking,
};
