// Authentication Routes

const express = require('express');
const router = express.Router();
const { register, login, logout, getCurrentUser, updateProfile } = require('../controllers/authController');
const { requireLogin } = require('../middleware/auth');
const multer = require('multer');

// Configure multer for file uploads
const upload = multer({
  dest: '../static/profiles/',
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed'));
    }
  },
});

// POST /api/auth/register
router.post('/register', register);

// POST /api/auth/login
router.post('/login', login);

// POST /api/auth/logout
router.post('/logout', requireLogin, logout);

// GET /api/auth/current-user
router.get('/current-user', getCurrentUser);

// POST /api/auth/profile
router.post('/profile', requireLogin, upload.single('photo'), updateProfile);

module.exports = router;
