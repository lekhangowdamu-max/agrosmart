# AgroSmart - Local Development Setup

This guide explains how to run the entire AgroSmart project locally for development and testing.

---

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- MySQL Server 5.7+ installed
- Git installed

---

## Setup Instructions

### 1. Clone/Navigate to Project

```bash
cd /path/to/AgroSmart
```

### 2. Set Up Local Database

#### Option A: Using Local MySQL Server

```bash
# Start MySQL server (command varies by OS)

# Windows:
mysql.exe -u root -p

# macOS:
mysql -u root -p

# Linux:
sudo mysql -u root -p
```

#### Option B: Using Docker

```bash
docker run --name agrosmart-mysql \
  -e MYSQL_ROOT_PASSWORD=LEKHAN@2121 \
  -e MYSQL_DATABASE=agrosmart \
  -p 3306:3306 \
  -d mysql:8.0
```

### 3. Initialize Database Schema

```bash
# Copy database/schema.sql to a file or directly execute in MySQL client
mysql -u root -p agrosmart < database/schema.sql
```

Or manually in MySQL:
```sql
mysql> USE agrosmart;
mysql> -- Copy and run all SQL from database/schema.sql file
```

### 4. Create .env File

Create a `.env` file in the root directory (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your local settings:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=LEKHAN@2121
DB_NAME=agrosmart
SECRET_KEY=dev-secret-key-change-in-production
GOOGLE_MAPS_API_KEY=AIzaSyD-2rQJtoNtSKxnI9ExHnGAd_CuKK7yj1Q
```

---

## Running the Application

### Option 1: Run Everything Together (Recommended for Testing)

#### Terminal 1 - Flask Backend (Main App)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run Flask app
python app.py
# Or: flask run

# App runs on http://localhost:5000
```

#### Terminal 2 - Drone Backend (Node.js)

```bash
cd drone-control-system/backend

# Install dependencies
npm install

# Run with nodemon (auto-reload)
npm run dev
# Or: npm start

# Server runs on http://localhost:4000
```

#### Terminal 3 - Drone Frontend (React + Vite)

```bash
cd drone-control-system/frontend

# Install dependencies
npm install

# Run development server
npm run dev

# App runs on http://localhost:5173
```

### Option 2: Run Only Flask Backend

```bash
pip install -r requirements.txt
python app.py
# Access at http://localhost:5000
```

### Option 3: Run Only Drone System

```bash
# Terminal 1
cd drone-control-system/backend
npm install
npm run dev

# Terminal 2
cd drone-control-system/frontend
npm install
npm run dev
```

---

## Testing Builds

### Test Flask Backend Build

```bash
# Verify dependencies can be installed
pip install -r requirements.txt

# Check for syntax errors
python -m py_compile app.py

# Verify WSGI entry point
python wsgi.py
```

### Test Drone Backend Build

```bash
cd drone-control-system/backend
npm install
npm run build 2>&1 || echo "No build script needed for Node backend"
npm run dev
```

### Test Drone Frontend Build

```bash
cd drone-control-system/frontend
npm install
npm run build

# Check that dist/ folder was created
ls -la dist/
```

---

## Accessing the Application

### Main Web Application
- **URL:** http://localhost:5000
- **Features:** 
  - Login/Register page
  - User dashboard
  - Machinery booking
  - Admin panel
  - Weather & prices

### Drone Control System
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:4000
- **Features:**
  - Real-time drone dashboard
  - Joystick control
  - Telemetry monitoring
  - Map display

---

## Development Commands

### Python Backend

```bash
# Install specific package
pip install package_name

# Update requirements
pip freeze > requirements.txt

# Run tests
python -m pytest

# Format code
black app.py

# Check for issues
pylint app.py
```

### Node Backend

```bash
# Update packages
npm update

# Install specific package
npm install package_name --save

# Remove package
npm uninstall package_name
```

### React Frontend

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Analyze bundle size
npm run build -- --analyze
```

---

## Troubleshooting

### "Could not connect to database"

```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1;"

# Verify credentials in .env file
# Recreate database if needed
mysql -u root -p < database/schema.sql
```

### "Port 5000 already in use"

```bash
# Find process using port 5000
lsof -i :5000

# Kill the process (macOS/Linux)
kill -9 <PID>

# Or run Flask on different port
flask run --port 5001
```

### "Module 'xyz' not found"

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or install individual package
pip install package_name
```

### "npm packages not found"

```bash
# Clear npm cache
npm cache clean --force

# Reinstall
npm install
```

### Socket.io Connection Issues

```bash
# Check that both servers are running
# Backend (Flask): http://localhost:5000
# Drone Backend: http://localhost:4000
# Drone Frontend: http://localhost:5173

# Verify CORS settings in drone-control-system/backend/src/index.js
```

---

## File Upload Testing

The app supports file uploads for:
- User profile photos
- Vehicle images
- Machinery images

Test locally:
1. Go to http://localhost:5000/profile
2. Try uploading a JPG/PNG file
3. Files saved to `static/uploads/`

---

## Database Inspection

### Using MySQL CLI

```bash
# Connect to database
mysql -u root -p agrosmart

# Show all tables
SHOW TABLES;

# View users
SELECT * FROM users;

# View machinery
SELECT * FROM machinery;

# View bookings
SELECT * FROM bookings;
```

### Using MySQL Workbench

1. Download MySQL Workbench
2. Create connection to localhost:3306
3. Connect with user `root` and password `LEKHAN@2121`
4. Navigate to `agrosmart` database
5. Browse tables visually

---

## Performance Testing

### Load Testing Flask App

```bash
# Install Apache Bench
# macOS: brew install httpd
# Linux: sudo apt-get install apache2-utils
# Windows: Download from Apache website

ab -n 100 -c 10 http://localhost:5000/
```

### Monitor Memory/CPU

```bash
# macOS/Linux
top

# Windows (Task Manager)
# Or: wmic OS get TotalVisibleMemorySize,FreePhysicalMemory
```

---

## Production Build Testing

### Test Flask Production Build

```bash
# Use Gunicorn (WSGI server)
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
```

### Test Drone Frontend Production Build

```bash
cd drone-control-system/frontend

# Build
npm run build

# Preview production build
npm run preview
# Runs on http://localhost:4173
```

---

## Git Setup

```bash
# Initialize if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial AgroSmart setup with deployment configs"

# Add remote (if pushing to GitHub)
git remote add origin https://github.com/yourusername/agrosmart.git
git push -u origin main
```

---

## Next Steps

1. Develop and test locally
2. When ready, follow [DEPLOYMENT.md](DEPLOYMENT.md) for Vercel deployment
3. Use `git push` to update your repository
4. Redeploy on Vercel (automatic with GitHub integration)

---

## Tips

- Always run migrations/schema setup after pulling database changes
- Use `.gitignore` to exclude `.env` and `__pycache__`
- Keep local database in sync with production (backup first)
- Test on multiple browsers for compatibility
- Monitor error logs: `vercel logs <url>`

