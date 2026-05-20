# Quick Start Guide for AgroSmart Node.js Backend

## 📋 Prerequisites

- Node.js 16+ 
- npm (comes with Node.js)
- MySQL 8.0+
- Git (optional)

## ⚡ Quick Setup (5 minutes)

### Step 1: Navigate to Backend Directory
```bash
cd node-backend
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Setup Environment Variables
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your database credentials
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

### Step 4: Create Database
```bash
# Login to MySQL
mysql -u root -p

# In MySQL console:
source database_schema.sql;
exit;
```

Or use a GUI tool like MySQL Workbench or phpMyAdmin.

### Step 5: Start Server
```bash
npm run dev
```

Server will start at: **http://localhost:3000**

## 🗄️ Database Setup (Detailed)

### Using MySQL Command Line

```bash
# Connect to MySQL
mysql -u root -p

# Execute the schema
SOURCE /path/to/database_schema.sql;

# Verify tables were created
SHOW TABLES;
```

### Using GUI Tools

**MySQL Workbench:**
1. Open MySQL Workbench
2. Open a new SQL Editor
3. Copy contents of `database_schema.sql`
4. Execute the query (Ctrl+Enter)

**phpMyAdmin:**
1. Go to phpMyAdmin (usually http://localhost/phpmyadmin)
2. Click "Import" tab
3. Select `database_schema.sql`
4. Click "Import"

## 🚀 Running the Server

### Development Mode (with auto-reload)
```bash
npm run dev
```
Server reloads on file changes

### Production Mode
```bash
npm start
```

### Testing the Server
```bash
# Check if server is running
curl http://localhost:3000/health

# Response should be:
# {"status":"ok","timestamp":"2024-01-01T12:00:00.000Z"}
```

## 📝 Environment Variables Explained

```
DB_HOST=localhost              # Database server address
DB_PORT=3306                   # MySQL port
DB_USER=root                   # MySQL username
DB_PASSWORD=password           # MySQL password
DB_NAME=agrosmart              # Database name

PORT=3000                      # Server port
NODE_ENV=development           # Environment (development/production)
SECRET_KEY=your-secret         # For password hashing
SESSION_SECRET=your-secret     # For session management
SESSION_COOKIE_SECURE=false    # Use true with HTTPS only
```

## 🔄 Connecting Frontend

The frontend can connect by changing API base URL:

```javascript
// In your frontend JavaScript, change:
// FROM: http://localhost:5000/api
// TO:   http://localhost:3000/api
```

Or configure proxy in frontend:

```javascript
// axios or fetch example
const API_URL = 'http://localhost:3000';

fetch(`${API_URL}/api/machinery`)
  .then(res => res.json())
  .then(data => console.log(data));
```

## 📂 Project Structure

```
node-backend/
├── config/          - Database configuration
├── controllers/     - Business logic
├── routes/          - API endpoints
├── middleware/      - Authentication, error handling
├── utilities/       - Helper functions
├── server.js        - Main entry point
├── package.json     - Dependencies
├── .env.example     - Environment template
└── database_schema.sql - Database setup
```

## ✅ Verify Installation

```bash
# Test 1: Server running
curl http://localhost:3000/health

# Test 2: Database connected
curl http://localhost:3000/api/machinery

# Test 3: User registration
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "role": "farmer"
  }'
```

## 🐛 Troubleshooting

### Port 3000 already in use

```bash
# Windows: Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux: Kill process on port 3000
lsof -i :3000
kill -9 <PID>

# Or change port in .env:
PORT=3001
```

### Database connection failed

```bash
# Check MySQL is running
# Windows: Services > MySQL80 > Start
# Mac: brew services start mysql
# Linux: sudo systemctl start mysql

# Verify credentials in .env
# Test connection
mysql -h localhost -u root -p -e "SELECT 1"
```

### Module not found errors

```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Session not working

1. Check browser accepts cookies
2. Verify `SESSION_SECRET` is set in .env
3. Clear browser cookies and try again
4. In Chrome DevTools > Application > Cookies

## 📚 API Documentation

See `README.md` for full API documentation with examples.

## 🔐 Security Checklist

Before production:
- [ ] Change `SECRET_KEY` in .env
- [ ] Change `SESSION_SECRET` in .env
- [ ] Set `SESSION_COOKIE_SECURE=true` (requires HTTPS)
- [ ] Set `NODE_ENV=production`
- [ ] Update database user credentials
- [ ] Use strong MySQL password
- [ ] Enable HTTPS (let's encrypt)
- [ ] Set proper CORS_ORIGIN

## 📞 Getting Help

1. Check server logs in terminal
2. Review `README.md` for full documentation
3. Check browser console for frontend errors
4. Verify `.env` configuration
5. Test API endpoints with curl or Postman

## 🎯 Next Steps

1. Verify all features work
2. Update frontend API endpoints
3. Test with actual data
4. Deploy to production server
5. Setup monitoring and logging

---

**Happy farming with AgroSmart! 🌾**
