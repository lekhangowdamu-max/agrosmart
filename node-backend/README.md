# AgroSmart Backend - Node.js + Express

A production-ready Node.js and Express.js backend for the AgroSmart agricultural machinery rental platform. This backend replaces the Python Flask application while maintaining 100% compatibility with the existing frontend.

## Features

✅ **User Management**
- User registration and login with bcrypt hashing
- Role-based access control (Farmer, Admin)
- Profile management with photo upload
- Session-based authentication

✅ **Machinery Management**
- Browse available machinery
- Machinery details and pricing
- Admin machinery management (CRUD)

✅ **Booking System**
- Create machinery bookings with date selection
- Booking status tracking (pending, approved, rejected, cancelled)
- Cost calculation based on dates and pricing
- Admin booking approval workflow
- Booking cancellation

✅ **Admin Dashboard**
- Dashboard statistics and analytics
- Pending bookings review
- Booking approval/rejection
- Top booked machinery tracking
- Approved bookings for vehicle tracking

✅ **Crop Market Prices**
- Browse crop prices by state, district, commodity
- Price history charts
- Kannada language support for crops
- Admin price management

✅ **IoT Support**
- Water motor control endpoints (ESP8266 compatible)
- Drone telemetry tracking
- Drone command logging
- Real-time status updates

✅ **Map & Location Services**
- User location tracking
- Location-based machinery search
- GPS coordinates for major cities

✅ **Utilities**
- Weather information endpoint
- CCTV monitoring endpoint
- Real-time data endpoints for mobile apps

## Technology Stack

- **Runtime**: Node.js 16+
- **Framework**: Express.js 4.18
- **Database**: MySQL 8.0+
- **Authentication**: bcryptjs + express-session
- **Validation**: express-validator
- **File Upload**: multer
- **Security**: helmet, CORS
- **Environment**: dotenv
- **ODM/ORM**: Direct MySQL queries (mysql2/promise)

## Installation

### 1. Prerequisites

- Node.js 16 or higher
- npm or yarn
- MySQL 8.0 or higher

### 2. Setup Instructions

```bash
# Navigate to the node-backend directory
cd node-backend

# Install dependencies
npm install

# Create .env file from example
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

### 3. Database Setup

```bash
# Import the database schema
mysql -u root -p < database_schema.sql

# Or manually execute the schema in MySQL:
# 1. Open MySQL client
mysql -u root -p
# 2. Execute the schema file
source database_schema.sql;
```

### 4. Environment Configuration

Edit `.env` file:

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=agrosmart

# Server
PORT=3000
NODE_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production

# Session
SESSION_SECRET=your-session-secret-change-this-in-production
SESSION_COOKIE_SECURE=false  # Set to true in production with HTTPS

# CORS
CORS_ORIGIN=*

# Database Pool
DB_POOL_SIZE=10
DB_CONNECTION_TIMEOUT=10000
```

### 5. Start the Server

```bash
# Development mode with nodemon
npm run dev

# Production mode
npm start
```

The server will start on `http://localhost:3000`

## Project Structure

```
node-backend/
├── config/
│   └── database.js           # MySQL connection pool
├── controllers/
│   ├── authController.js     # Authentication logic
│   ├── machineryController.js
│   ├── bookingController.js
│   ├── adminController.js
│   ├── pricesController.js
│   └── utilitiesController.js
├── middleware/
│   ├── auth.js               # Authentication middleware
│   └── errorHandler.js       # Error handling
├── routes/
│   ├── auth.js
│   ├── machinery.js
│   ├── bookings.js
│   ├── admin.js
│   ├── prices.js
│   └── utilities.js
├── utilities/
│   └── helpers.js            # Utility functions
├── server.js                 # Main server file
├── package.json
├── .env.example
└── database_schema.sql
```

## API Endpoints

### Authentication

```
POST   /api/auth/register              # Register new user
POST   /api/auth/login                 # User login
POST   /api/auth/logout                # User logout
GET    /api/auth/current-user          # Get current user
POST   /api/auth/profile               # Update user profile
```

### Machinery

```
GET    /api/machinery                  # Get all machinery
GET    /api/machinery/:machineId       # Get machinery details
POST   /api/machinery                  # Create machinery (admin)
PUT    /api/machinery/:machineId       # Update machinery (admin)
DELETE /api/machinery/:machineId       # Delete machinery (admin)
```

### Bookings

```
POST   /api/bookings                   # Create booking
GET    /api/bookings                   # Get user bookings
GET    /api/bookings/:bookingId        # Get booking details
POST   /api/bookings/:bookingId/cancel # Cancel booking
GET    /api/bookings/:bookingId/track  # Get booking tracking info
```

### Admin

```
GET    /api/admin/stats                # Dashboard statistics
GET    /api/admin/bookings             # Get all bookings
GET    /api/admin/bookings/pending     # Get pending bookings
GET    /api/admin/bookings/approved    # Get approved bookings
POST   /api/admin/bookings/:id/approve # Approve booking
POST   /api/admin/bookings/:id/reject  # Reject booking
```

### Prices

```
GET    /api/prices                     # Get crop prices (with filters)
GET    /api/prices/states              # Get all states
GET    /api/prices/districts           # Get districts for state
GET    /api/prices/commodities         # Get commodities for district
GET    /api/prices/history             # Get price history
POST   /api/prices                     # Add crop price (admin)
```

### Utilities

```
GET    /api/map                        # Get map data
GET    /api/weather                    # Get weather data
GET    /api/motor                      # Get motor status
POST   /api/motor/control              # Control motor
GET    /api/drone/telemetry            # Get drone telemetry
POST   /api/drone/telemetry            # Update drone telemetry
GET    /api/drone/logs                 # Get drone logs
POST   /api/drone/logs                 # Add drone log
GET    /api/cctv                       # Get CCTV status
```

## Request/Response Examples

### Register User

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Farmer",
    "email": "john@example.com",
    "password": "secure_password",
    "role": "farmer",
    "phone": "9999999999",
    "location": "Bangalore"
  }'
```

Response:
```json
{
  "message": "Registration successful",
  "userId": 1
}
```

### Login User

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure_password"
  }'
```

Response:
```json
{
  "message": "Login successful",
  "user": {
    "userId": 1,
    "name": "John Farmer",
    "email": "john@example.com",
    "role": "farmer",
    "location": "Bangalore",
    "photo": null
  }
}
```

### Create Booking

```bash
curl -X POST http://localhost:3000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "machineId": 1,
    "startDate": "2024-06-15",
    "endDate": "2024-06-17",
    "notes": "Need tractor for field preparation"
  }'
```

Response:
```json
{
  "message": "Booking request submitted successfully",
  "bookingId": 1,
  "totalCost": 1000
}
```

## Error Handling

All API endpoints return standardized error responses:

```json
{
  "error": "Error message description"
}
```

Common HTTP Status Codes:
- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate entry (e.g., email already exists)
- `500 Internal Server Error` - Server error

## Security Features

✅ Password hashing with bcryptjs (10 salt rounds)
✅ Session-based authentication with httpOnly cookies
✅ Role-based access control (RBAC)
✅ CORS protection
✅ SQL injection prevention (parameterized queries)
✅ Environment variable protection (.env)
✅ Secure headers with helmet
✅ Input validation and sanitization

## IoT Integration

### Motor Control (ESP8266)

Endpoints for water motor control systems:

```
GET  /api/motor          # Get current motor status
POST /api/motor/control  # Send motor command
```

Example IoT command:
```json
{
  "action": "on",
  "power": 100
}
```

### Drone Communication

Endpoints for drone telemetry and logging:

```
GET  /api/drone/telemetry      # Get latest drone data
POST /api/drone/telemetry      # Update drone telemetry
GET  /api/drone/logs           # Get drone event logs
POST /api/drone/logs           # Add drone event
```

## Deployment

### Vercel Deployment

Create `vercel.json` in the root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "server.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "server.js"
    }
  ],
  "env": {
    "DB_HOST": "@db_host",
    "DB_USER": "@db_user",
    "DB_PASSWORD": "@db_password",
    "DB_NAME": "agrosmart",
    "SESSION_SECRET": "@session_secret"
  }
}
```

Deploy:
```bash
vercel --prod
```

### Heroku Deployment

```bash
heroku create agrosmart-backend
heroku config:set DB_HOST=your_db_host
heroku config:set DB_USER=your_db_user
heroku config:set DB_PASSWORD=your_db_password
heroku config:set SESSION_SECRET=your_secret
git push heroku main
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t agrosmart-backend .
docker run -p 3000:3000 --env-file .env agrosmart-backend
```

## Performance Optimization

✅ Database connection pooling (max 10 connections)
✅ Efficient database queries with proper indexing
✅ Session management with configurable timeout
✅ Static file caching headers
✅ Request body size limit configuration
✅ Async error handling to prevent crashes

## Monitoring & Logging

The server logs:
- Request method and path
- Database connection status
- Error stack traces
- Session operations

For production, integrate with:
- Winston for advanced logging
- Sentry for error tracking
- DataDog for performance monitoring

## Frontend Compatibility

✅ All existing HTML templates work without modification
✅ Session cookies compatible with JavaScript fetch
✅ CORS enabled for cross-origin requests
✅ Static file serving for CSS and images
✅ Form submission handling with JSON responses

## Migration from Flask

The conversion maintains all Flask functionality:
- Same database schema (MySQL)
- Same authentication flow
- Same API response structure
- Same file upload handling
- Same error messages
- Same business logic

## Testing

Run tests (Jest configured):

```bash
npm test
```

## Contributing

1. Follow the existing code structure
2. Use async/await for database operations
3. Implement proper error handling
4. Add validation for all inputs
5. Update documentation for new endpoints

## Troubleshooting

### Database Connection Error

```
Error: Database connection failed
```

**Solution**: Check `.env` file settings and MySQL service is running

```bash
# Check MySQL status
sudo systemctl status mysql

# Check connection
mysql -h localhost -u root -p -e "SELECT 1"
```

### Port Already in Use

```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution**: Change PORT in `.env` or kill existing process

```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :3000
kill -9 <PID>
```

### Session Not Persisting

Check browser cookies are enabled and `SESSION_COOKIE_SECURE` is correct for your environment.

## License

MIT License - See LICENSE file

## Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation
- Check database schema
- Verify environment configuration

---

**Converted from Python Flask to Node.js/Express**
Maintains 100% frontend compatibility | Production-ready | IoT support included
