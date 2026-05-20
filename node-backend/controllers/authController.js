// Authentication Controller

const pool = require('../config/database');
const { hashPassword, verifyPassword, validateEmail, generateSessionData } = require('../utilities/helpers');
const fs = require('fs');
const path = require('path');

// User registration
const register = async (req, res, next) => {
  try {
    const { name, email, password, role, phone, location } = req.body;

    // Validation
    if (!name || !email || !password) {
      return res.status(400).json({ error: 'Name, email, and password are required' });
    }

    if (!validateEmail(email)) {
      return res.status(400).json({ error: 'Invalid email format' });
    }

    if (password.length < 6) {
      return res.status(400).json({ error: 'Password must be at least 6 characters' });
    }

    // Check if email already exists
    const [existingUsers] = await pool.query(
      'SELECT id FROM users WHERE email = ?',
      [email]
    );

    if (existingUsers.length > 0) {
      return res.status(409).json({ error: 'Email already registered' });
    }

    // Hash password
    const hashedPassword = await hashPassword(password);

    // Create user
    const userRole = (role === 'admin' || role === 'farmer') ? role : 'farmer';
    const [result] = await pool.query(
      'INSERT INTO users (name, email, password, role, phone, location, phone_verified) VALUES (?, ?, ?, ?, ?, ?, ?)',
      [name, email, hashedPassword, userRole, phone || null, location || null, false]
    );

    res.status(201).json({
      message: 'Registration successful',
      userId: result.insertId,
    });
  } catch (error) {
    next(error);
  }
};

// User login
const login = async (req, res, next) => {
  try {
    const { email, password } = req.body;

    // Validation
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    // Get user by email
    const [users] = await pool.query(
      'SELECT id, name, email, password, role, location, photo FROM users WHERE email = ?',
      [email]
    );

    if (users.length === 0) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const user = users[0];

    // Verify password
    const passwordMatch = await verifyPassword(password, user.password);
    if (!passwordMatch) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    // Create session
    req.session.userId = user.id;
    req.session.name = user.name;
    req.session.email = user.email;
    req.session.role = user.role;
    req.session.location = user.location;
    req.session.photo = user.photo;

    res.json({
      message: 'Login successful',
      user: generateSessionData(user),
    });
  } catch (error) {
    next(error);
  }
};

// User logout
const logout = (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Logout failed' });
    }
    res.json({ message: 'Logged out successfully' });
  });
};

// Get current user
const getCurrentUser = (req, res) => {
  if (!req.session || !req.session.userId) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  res.json({
    user: {
      userId: req.session.userId,
      name: req.session.name,
      email: req.session.email,
      role: req.session.role,
      location: req.session.location,
      photo: req.session.photo,
    },
  });
};

// Update profile
const updateProfile = async (req, res, next) => {
  try {
    if (!req.session || !req.session.userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { name, email, phone, location } = req.body;
    const userId = req.session.userId;

    // Validation
    if (!name || !email) {
      return res.status(400).json({ error: 'Name and email are required' });
    }

    // Check if email is already taken by another user
    const [existingUsers] = await pool.query(
      'SELECT id FROM users WHERE email = ? AND id != ?',
      [email, userId]
    );

    if (existingUsers.length > 0) {
      return res.status(409).json({ error: 'Email already registered' });
    }

    // Handle profile photo upload
    let photoPath = null;
    if (req.file) {
      const uploadDir = path.join(__dirname, '../public/uploads/profiles');
      if (!fs.existsSync(uploadDir)) {
        fs.mkdirSync(uploadDir, { recursive: true });
      }
      photoPath = `profiles/${req.file.filename}`;
    }

    // Update user
    const updates = [];
    const values = [];

    updates.push('name = ?');
    values.push(name);
    updates.push('email = ?');
    values.push(email);

    if (phone) {
      updates.push('phone = ?');
      values.push(phone);
    }

    if (location) {
      updates.push('location = ?');
      values.push(location);
    }

    if (photoPath) {
      updates.push('photo = ?');
      values.push(photoPath);
    }

    updates.push('updated_at = NOW()');
    values.push(userId);

    await pool.query(
      `UPDATE users SET ${updates.join(', ')} WHERE id = ?`,
      values
    );

    // Update session
    req.session.name = name;
    req.session.email = email;
    req.session.location = location;
    if (photoPath) {
      req.session.photo = photoPath;
    }

    res.json({
      message: 'Profile updated successfully',
      user: {
        name,
        email,
        phone,
        location,
        photo: photoPath || req.session.photo,
      },
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  register,
  login,
  logout,
  getCurrentUser,
  updateProfile,
};
