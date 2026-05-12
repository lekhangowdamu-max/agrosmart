# AgroSmart - Build Verification Guide

This document provides step-by-step instructions to verify that the AgroSmart project is ready for Vercel deployment.

---

## Pre-Deployment Checklist

### ✅ Files Created/Modified

- [x] `requirements.txt` - Updated with all Python dependencies
- [x] `wsgi.py` - Created for WSGI/Vercel compatibility
- [x] `vercel.json` - Created for Flask backend deployment
- [x] `app.py` - Updated to support environment variables
- [x] `.env.example` - Created with all required environment variables
- [x] `.gitignore` - Created to exclude sensitive files
- [x] `DEPLOYMENT.md` - Created with complete deployment guide
- [x] `LOCAL_SETUP.md` - Created with local development guide
- [x] `drone-control-system/backend/vercel.json` - Created
- [x] `drone-control-system/backend/.env.example` - Updated
- [x] `drone-control-system/frontend/vercel.json` - Created
- [x] `drone-control-system/frontend/.env.example` - Updated

---

## Verification Steps

### 1. Flask Backend Verification

#### 1.1 Check Requirements

```bash
# Navigate to project root
cd /path/to/AgroSmart

# Verify requirements.txt format
cat requirements.txt

# Expected output:
# Flask==2.3.3
# Werkzeug==2.3.7
# mysql-connector-python==8.1.0
# requests==2.31.0
# beautifulsoup4==4.12.2
# python-dotenv==1.0.0
# gunicorn==21.2.0
# click==8.1.7
# Jinja2==3.1.2
# MarkupSafe==2.1.3
```

✅ **Status:** All dependencies listed with specific versions

#### 1.2 Verify WSGI Entry Point

```bash
# Check wsgi.py exists
test -f wsgi.py && echo "✓ wsgi.py exists" || echo "✗ wsgi.py missing"

# Check wsgi.py content
head -5 wsgi.py
# Should show: import os, sys, from app import app
```

✅ **Status:** wsgi.py created and properly imports Flask app

#### 1.3 Check vercel.json Configuration

```bash
# Verify Flask vercel.json
cat vercel.json

# Should contain:
# - builds section with wsgi.py and @vercel/python
# - routes section routing to wsgi.py
# - environment variables
```

✅ **Status:** vercel.json properly configured for Flask

#### 1.4 Verify app.py Environment Variables Support

```bash
# Check for environment variable usage in app.py
grep -n "os.getenv" app.py

# Expected lines:
# Line ~14: app.secret_key = os.getenv("SECRET_KEY", ...)
# Line ~16: GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", ...)
# Lines ~44-48: Database config uses os.getenv for DB credentials
```

✅ **Status:** app.py supports environment variables

---

### 2. Drone Backend (Node.js) Verification

#### 2.1 Check package.json

```bash
cd drone-control-system/backend

# Verify scripts are present
cat package.json | grep -A 5 '"scripts"'

# Should include:
# - "start": "node src/index.js"
# - "dev": "nodemon src/index.js"

# Verify dependencies
cat package.json | grep -A 10 '"dependencies"'

# Should include: express, socket.io, cors, dotenv
```

✅ **Status:** package.json correctly configured

#### 2.2 Check Vercel Configuration for Drone Backend

```bash
# Check if vercel.json exists
test -f vercel.json && echo "✓ vercel.json exists" || echo "✗ missing"

# Verify content
cat vercel.json

# Should show:
# - build using @vercel/node
# - entry point: src/index.js
# - routes to src/index.js
```

✅ **Status:** Drone backend vercel.json exists

#### 2.3 Check .env.example

```bash
cat .env.example

# Should include:
# - PORT
# - NODE_ENV
# - FRONTEND_URL
# - DRONE_NAME
```

✅ **Status:** .env.example configured

---

### 3. Drone Frontend (React + Vite) Verification

#### 3.1 Check package.json

```bash
cd drone-control-system/frontend

# Verify build script exists
cat package.json | grep -A 5 '"scripts"'

# Should include: "build": "vite build"
```

✅ **Status:** Build script present

#### 3.2 Check vite.config.js

```bash
# Verify vite config exists
test -f vite.config.js && echo "✓ vite.config.js exists"

# Check React plugin is configured
grep -i "react" vite.config.js && echo "✓ React plugin found"
```

✅ **Status:** Vite configuration correct

#### 3.3 Check Vercel Configuration for Frontend

```bash
# Check vercel.json
test -f vercel.json && echo "✓ vercel.json exists" || echo "✗ missing"

# Verify outputDirectory is set to dist
grep "outputDirectory" vercel.json
# Should output: "outputDirectory": "dist"
```

✅ **Status:** Frontend vercel.json configured

---

### 4. Database Configuration Verification

#### 4.1 Check Database Schema

```bash
# Navigate to database folder
cd database

# Verify schema.sql exists
test -f schema.sql && echo "✓ schema.sql found"

# Check schema content
head -10 schema.sql

# Should contain:
# - CREATE DATABASE agrosmart
# - CREATE TABLE users
# - CREATE TABLE machinery
# - CREATE TABLE bookings
```

✅ **Status:** Database schema available

---

### 5. Environment Variables Verification

#### 5.1 Main Backend Environment

```bash
# Check .env.example exists in root
test -f .env.example && echo "✓ .env.example found"

# Verify required variables
grep "DB_HOST" .env.example && echo "✓ DB_HOST present"
grep "DB_USER" .env.example && echo "✓ DB_USER present"
grep "DB_PASSWORD" .env.example && echo "✓ DB_PASSWORD present"
grep "SECRET_KEY" .env.example && echo "✓ SECRET_KEY present"
```

✅ **Status:** Environment variables documented

---

### 6. File Structure Verification

```bash
# Verify all required files exist
echo "Checking file structure..."

test -f requirements.txt && echo "✓ requirements.txt"
test -f wsgi.py && echo "✓ wsgi.py"
test -f vercel.json && echo "✓ vercel.json (root)"
test -f app.py && echo "✓ app.py"
test -f .env.example && echo "✓ .env.example"
test -f .gitignore && echo "✓ .gitignore"
test -f DEPLOYMENT.md && echo "✓ DEPLOYMENT.md"
test -f LOCAL_SETUP.md && echo "✓ LOCAL_SETUP.md"

test -f drone-control-system/backend/vercel.json && echo "✓ drone/backend/vercel.json"
test -f drone-control-system/backend/package.json && echo "✓ drone/backend/package.json"
test -f drone-control-system/backend/.env.example && echo "✓ drone/backend/.env.example"

test -f drone-control-system/frontend/vercel.json && echo "✓ drone/frontend/vercel.json"
test -f drone-control-system/frontend/package.json && echo "✓ drone/frontend/package.json"
test -f drone-control-system/frontend/vite.config.js && echo "✓ drone/frontend/vite.config.js"

test -f database/schema.sql && echo "✓ database/schema.sql"
```

✅ **Status:** All required files present

---

## Build Simulation

### Python Backend Build Test

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify imports work
python -c "from app import app; print('✓ app.py imports successfully')"

# 3. Check wsgi module
python -c "from wsgi import app; print('✓ wsgi.py imports successfully')"

# 4. Verify Flask app is created
python -c "from app import app; print(f'✓ Flask app created: {type(app)}')"
```

**Expected Output:**
```
✓ app.py imports successfully
✓ wsgi.py imports successfully
✓ Flask app created: <class 'flask.app.Flask'>
```

### Node Backend Build Test

```bash
cd drone-control-system/backend

# 1. Install dependencies
npm install

# 2. Verify main entry point
node -c src/index.js

# 3. Check Express app creation (if possible without running)
npm run dev &
PID=$!
sleep 2
kill $PID
```

### React Frontend Build Test

```bash
cd drone-control-system/frontend

# 1. Install dependencies
npm install

# 2. Build production version
npm run build

# 3. Verify dist folder created
test -d dist && echo "✓ dist folder created" && ls dist/
```

---

## Deployment Readiness Checklist

- [x] Python dependencies installed and verified
- [x] WSGI entry point (wsgi.py) created
- [x] vercel.json files created for all three services
- [x] Environment variables support added to app.py
- [x] .env.example files created with all required variables
- [x] Database schema available
- [x] No hardcoded credentials in app.py
- [x] File structure matches Vercel expectations
- [x] Build scripts configured in package.json files
- [x] .gitignore properly configured

---

## Deployment Instructions Summary

### 1. Set Up Database

- Create MySQL database on PlanetScale, AWS RDS, or similar
- Run `database/schema.sql` to initialize tables
- Note connection credentials

### 2. Configure Environment Variables in Vercel

#### Flask Backend
```
DB_HOST=your-database-host
DB_USER=your-database-user
DB_PASSWORD=your-secure-password
DB_NAME=agrosmart
SECRET_KEY=generate-random-key
GOOGLE_MAPS_API_KEY=your-api-key
```

#### Drone Backend
```
FRONTEND_URL=https://your-drone-frontend.vercel.app
NODE_ENV=production
```

#### Drone Frontend
```
VITE_BACKEND_URL=https://your-drone-backend.vercel.app
VITE_APP_BACKEND_URL=https://your-flask-backend.vercel.app
VITE_DRONE_SERVER_URL=https://your-drone-backend.vercel.app
```

### 3. Deploy Each Service

```bash
# Option A: Using Vercel CLI
vercel deploy --prod

# Option B: Push to GitHub and link in Vercel Dashboard
git push origin main
```

### 4. Verify Deployments

- Flask Backend: `https://your-flask.vercel.app/` - Should load homepage
- Drone Backend: `https://your-drone-backend.vercel.app/` - Should return JSON
- Drone Frontend: `https://your-drone-frontend.vercel.app/` - Should load React app

---

## Troubleshooting

### If build fails:

1. Check Vercel logs: `vercel logs <deployment-url>`
2. Verify all environment variables are set
3. Check that database is accessible
4. Ensure requirements.txt has all dependencies
5. Verify Python/Node versions compatibility

### Common Errors:

- **"Could not import app.py"** → Check wsgi.py exists and has correct imports
- **"FUNCTION_INVOCATION_FAILED"** → Check database connection in logs
- **"Module not found"** → Add to requirements.txt and rebuild
- **"Socket.io connection failed"** → Update CORS URLs in environment

---

## Next Steps

1. ✅ Verify this checklist is complete
2. Set up database with schema
3. Configure environment variables
4. Deploy to Vercel
5. Test all endpoints
6. Monitor logs for errors
7. Set up monitoring/alerts

