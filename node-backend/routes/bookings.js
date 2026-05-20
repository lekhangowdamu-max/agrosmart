// Bookings Routes

const express = require('express');
const router = express.Router();
const { createBooking, getUserBookings, getBookingById, cancelBooking, getBookingTracking } = require('../controllers/bookingController');
const { requireLogin } = require('../middleware/auth');

// POST /api/bookings
router.post('/', requireLogin, createBooking);

// GET /api/bookings
router.get('/', requireLogin, getUserBookings);

// GET /api/bookings/:bookingId
router.get('/:bookingId', requireLogin, getBookingById);

// POST /api/bookings/:bookingId/cancel
router.post('/:bookingId/cancel', requireLogin, cancelBooking);

// GET /api/bookings/:bookingId/track
router.get('/:bookingId/track', requireLogin, getBookingTracking);

module.exports = router;
