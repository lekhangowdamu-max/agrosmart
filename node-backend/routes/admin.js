// Admin Routes

const express = require('express');
const router = express.Router();
const { getDashboardStats, getPendingBookings, getAllBookings, getApprovedBookings, approveBooking, rejectBooking } = require('../controllers/adminController');
const { requireAdmin } = require('../middleware/auth');

// GET /api/admin/stats
router.get('/stats', requireAdmin, getDashboardStats);

// GET /api/admin/bookings/pending
router.get('/bookings/pending', requireAdmin, getPendingBookings);

// GET /api/admin/bookings
router.get('/bookings', requireAdmin, getAllBookings);

// GET /api/admin/bookings/approved
router.get('/bookings/approved', requireAdmin, getApprovedBookings);

// POST /api/admin/bookings/:bookingId/approve
router.post('/bookings/:bookingId/approve', requireAdmin, approveBooking);

// POST /api/admin/bookings/:bookingId/reject
router.post('/bookings/:bookingId/reject', requireAdmin, rejectBooking);

module.exports = router;
