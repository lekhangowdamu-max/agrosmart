// Authentication Middleware

const requireLogin = (req, res, next) => {
  if (!req.session || !req.session.userId) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  next();
};

const requireAdmin = (req, res, next) => {
  if (!req.session || !req.session.userId) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  if (req.session.role !== 'admin') {
    return res.status(403).json({ error: 'Admin privileges required' });
  }
  next();
};

const optionalUser = (req, res, next) => {
  // This middleware doesn't require authentication
  // User data will be available if logged in
  next();
};

module.exports = {
  requireLogin,
  requireAdmin,
  optionalUser,
};
