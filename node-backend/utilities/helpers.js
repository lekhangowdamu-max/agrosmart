// Utility Functions

const bcrypt = require('bcryptjs');

// Password hashing
const hashPassword = async (password) => {
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(password, salt);
};

const verifyPassword = async (password, hashedPassword) => {
  return bcrypt.compare(password, hashedPassword);
};

// Date formatting
const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Date(date).toISOString().split('T')[0];
};

const formatDateTime = (date) => {
  if (!date) return 'N/A';
  return new Date(date).toLocaleString();
};

// Validation functions
const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

const validatePhone = (phone) => {
  const re = /^\d{10}$/;
  return re.test(phone?.replace(/\D/g, ''));
};

// Calculate booking cost
const calculateBookingCost = (startDate, endDate, pricePerDay) => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
  return days * (pricePerDay || 0);
};

// Generate session data from user record
const generateSessionData = (user) => {
  return {
    userId: user.id,
    name: user.name,
    email: user.email,
    role: user.role,
    location: user.location,
    photo: user.photo,
  };
};

// Kannada crop names mapping
const kannadaNames = {
  'Rice': 'ಅಕ್ಕಿ',
  'Wheat': 'ಗೋಧಿ',
  'Maize': 'ಮೆಕ್ಕೆಜೋಳ',
  'Sugarcane': 'ಕಬ್ಬು',
  'Cotton': 'ಹತ್ತಿ',
  'Groundnut': 'ಕಡಲೆಕಾಯಿ',
  'Turmeric': 'ಅರಿಶಿನ',
  'Chilli': 'ಮೆಣಸಿನಕಾಯಿ',
};

const getKannadaName = (crop) => {
  return kannadaNames[crop] || crop;
};

// Location coordinates mapping
const locationCoordinates = {
  'Bangalore': [12.9716, 77.5946],
  'Mysore': [12.2958, 76.6394],
  'Hubli': [15.3647, 75.1240],
  'Belgaum': [15.8497, 74.4977],
  'Gulbarga': [17.3297, 76.8343],
  'Raichur': [16.2120, 77.3439],
  'Davangere': [14.4644, 75.9218],
  'Shimoga': [13.9299, 75.5681],
};

const getLocationCoordinates = (location) => {
  return locationCoordinates[location] || null;
};

module.exports = {
  hashPassword,
  verifyPassword,
  formatDate,
  formatDateTime,
  validateEmail,
  validatePhone,
  calculateBookingCost,
  generateSessionData,
  getKannadaName,
  getLocationCoordinates,
};
