// Admin Controller

const pool = require('../config/database');
const { formatDate } = require('../utilities/helpers');

// Get admin dashboard statistics
const getDashboardStats = async (req, res, next) => {
  try {
    if (!req.session || req.session.role !== 'admin') {
      return res.status(403).json({ error: 'Admin privileges required' });
    }

    // Get counts
    const [userCount] = await pool.query('SELECT COUNT(*) as count FROM users');
    const [machineryCount] = await pool.query('SELECT COUNT(*) as count FROM machinery');
    const [priceCount] = await pool.query('SELECT COUNT(*) as count FROM crop_prices');
    const [bookingCount] = await pool.query('SELECT COUNT(*) as count FROM bookings');
    const [pendingCount] = await pool.query('SELECT COUNT(*) as count FROM bookings WHERE status = "pending"');

    // Get top booked machines
    const [topMachines] = await pool.query(
      `SELECT m.name as machine_name, COUNT(b.id) as booking_count
       FROM machinery m
       LEFT JOIN bookings b ON m.id = b.machine_id
       GROUP BY m.id
       ORDER BY booking_count DESC
       LIMIT 5`
    );

    res.json({
      stats: {
        user_count: userCount[0].count,
        machinery_count: machineryCount[0].count,
        price_count: priceCount[0].count,
        booking_count: bookingCount[0].count,
        pending_bookings: pendingCount[0].count,
        top_machines: topMachines,
      },
    });
  } catch (error) {
    next(error);
  }
};

// Get pending bookings
const getPendingBookings = async (req, res, next) => {
  try {
    if (!req.session || req.session.role !== 'admin') {
      return res.status(403).json({ error: 'Admin privileges required' });
    }

    const [bookings] = await pool.query(
      `SELECT 
        b.id, b.start_date, b.end_date, b.total_cost, b.status, b.created_at, b.notes,
        u.id as user_id, u.name as user_name, u.email as user_email, u.location as user_location, u.phone as user_phone,
        m.id as machine_id, m.name as machine_name, m.location as machine_location
      FROM bookings b
      JOIN users u ON b.user_id = u.id
      JOIN machinery m ON b.machine_id = m.id
      WHERE b.status = 'pending'
      ORDER BY b.created_at DESC`
    );

    const formatted = bookings.map(b => ({
      id: b.id,
      user_name: b.user_name,
      user_email: b.user_email,
      user_location: b.user_location,
      user_phone: b.user_phone,
      machine_name: b.machine_name,
      machine_location: b.machine_location,
      start_date: formatDate(b.start_date),
      end_date: formatDate(b.end_date),
      total_cost: b.total_cost,
      created_at: b.created_at,
      notes: b.notes,
    }));

    res.json({
      bookings: formatted,
    });
  } catch (error) {
    next(error);
  }
};

// Get all bookings
const getAllBookings = async (req, res, next) => {
  try {
    if (!req.session || req.session.role !== 'admin') {
      return res.status(403).json({ error: 'Admin privileges required' });
    }

    const [bookings] = await pool.query(
      `SELECT 
        b.id, b.start_date, b.end_date, b.total_cost, b.status, b.created_at, b.notes,
        u.name as user_name, u.email as user_email, u.location as user_location,
        m.name as machine_name, m.location as machine_location
      FROM bookings b
      JOIN users u ON b.user_id = u.id
      JOIN machinery m ON b.machine_id = m.id
      ORDER BY b.created_at DESC`
    );

    const formatted = bookings.map(b => ({
      id: b.id,
      machine_name: b.machine_name,
      machine_location: b.machine_location,
      user_name: b.user_name,
      user_email: b.user_email,
      user_location: b.user_location,
      start_date: formatDate(b.start_date),
      end_date: formatDate(b.end_date),
      total_cost: b.total_cost || 0,
      status: b.status,
      created_at: b.created_at,
      notes: b.notes,
    }));

    res.json({
      bookings: formatted,
    });
  } catch (error) {
    next(error);
  }
};

// Get approved bookings (for tracking)
const getApprovedBookings = async (req, res, next) => {
  try {
    if (!req.session || req.session.role !== 'admin') {
      return res.status(403).json({ error: 'Admin privileges required' });
    }

    const [bookings] = await pool.query(
      `SELECT 
        b.id, b.start_date, b.end_date, b.total_cost, b.status, b.created_at, b.admin_location, 
        u.name as user_name, u.location as user_location,
        m.name as machine_name
      FROM bookings b
      JOIN users u ON b.user_id = u.id
      JOIN machinery m ON b.machine_id = m.id
      WHERE b.status = 'approved'
      ORDER BY b.created_at DESC`
    );

    const formatted = bookings.map(b => ({
      id: b.id,
      machine_name: b.machine_name,
      user_name: b.user_name,
      user_location: b.user_location,
      admin_location: b.admin_location,
      start_date: formatDate(b.start_date),
      end_date: formatDate(b.end_date),
      status: b.status,
    }));

    res.json({
      bookings: formatted,
    });
  } catch (error) {
    next(error);
  }
};

// Approve booking
const approveBooking = async (req, res, next) => {
  try {
    if (!req.session || req.session.role !== 'admin') {
      return res.status(403).json({ error: 'Admin privileges required' });
    }

    const { bookingId } = req.params;
    const { admin_phone, admin_vehicle_number, admin_location } = req.body;
    const adminId = req.session.userId;
    const adminPhoto = req.session.photo || null;

    // Get booking
    const [bookings] = await pool.query(
      'SELECT id FROM bookings WHERE id = ?',
      [bookingId]
    );

    if (bookings.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    // Update booking
    await pool.query(
      `UPDATE bookings SET 
        status = ?, 
        admin_phone = ?, 
        admin_vehicle_number = ?, 
        admin_location = ?, 
        admin_photo = ?,
        accepted_by_admin_id = ?,
        updated_at = NOW()
      WHERE id = ?`,
      ['approved', admin_phone || null, admin_vehicle_number || null, admin_location || null, adminPhoto, adminId, bookingId]
    );

    res.json({
      message: 'Booking approved successfully',
    });
  } catch (error) {
    next(error);
  }
};

// Reject booking
const rejectBooking = async (req, res, next) => {
  try {
    if (!req.session || req.session.role !== 'admin') {
      return res.status(403).json({ error: 'Admin privileges required' });
    }

    const { bookingId } = req.params;

    // Get booking
    const [bookings] = await pool.query(
      'SELECT id FROM bookings WHERE id = ?',
      [bookingId]
    );

    if (bookings.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    // Update booking
    await pool.query(
      'UPDATE bookings SET status = ?, updated_at = NOW() WHERE id = ?',
      ['rejected', bookingId]
    );

    res.json({
      message: 'Booking rejected successfully',
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getDashboardStats,
  getPendingBookings,
  getAllBookings,
  getApprovedBookings,
  approveBooking,
  rejectBooking,
};
