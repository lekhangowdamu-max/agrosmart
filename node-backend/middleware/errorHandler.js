// Error Handling Middleware

const errorHandler = (err, req, res, next) => {
  console.error('Error:', err.message);
  console.error('Stack:', err.stack);

  // Validation errors
  if (err.status === 400 && err.validation) {
    return res.status(400).json({
      error: 'Validation failed',
      details: err.validation,
    });
  }

  // Database errors
  if (err.code && (err.code.startsWith('ER_') || err.errno)) {
    console.error('Database error code:', err.code);
    if (err.code === 'ER_DUP_ENTRY') {
      return res.status(409).json({ error: 'Duplicate entry - email may already be registered' });
    }
    return res.status(503).json({ error: 'Database error occurred' });
  }

  // JSON parsing errors
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return res.status(400).json({ error: 'Invalid JSON' });
  }

  // Generic server errors
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error',
  });
};

const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

module.exports = {
  errorHandler,
  asyncHandler,
};
