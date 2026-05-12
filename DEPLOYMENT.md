# AgroSmart - Vercel Deployment Guide

This document explains how to deploy AgroSmart on Vercel. The project is a full-stack hybrid application with:
- **Flask Backend** (Python) - Main application server
- **Node.js Drone Server** (Express + Socket.io) - Real-time drone state management
- **React Frontend** (Vite) - Drone control dashboard
- **MySQL Database** - Data persistence

---

## Project Structure

```
AgroSmart/
├── app.py                          # Main Flask application
├── wsgi.py                         # WSGI entry point for Vercel
├── vercel.json                     # Flask backend Vercel config
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
│
└── drone-control-system/
    ├── backend/                    # Node.js drone server
    │   ├── src/index.js
    │   ├── package.json
    │   ├── vercel.json            # Drone backend Vercel config
    │   └── .env.example
    │
    └── frontend/                   # React + Vite drone dashboard
        ├── src/
        ├── package.json
        ├── vite.config.js
        ├── vercel.json            # Drone frontend Vercel config
        └── .env.example
```

---

## Prerequisites

- **Vercel Account** - https://vercel.com (free tier available)
- **MySQL Database** - You'll need a cloud MySQL service:
  - **Option 1:** AWS RDS
  - **Option 2:** MySQL on PlanetScale (free tier: https://planetscale.com)
  - **Option 3:** ClearDB on Heroku
  - **Option 4:** Google Cloud SQL

---

## Step 1: Prepare Database

### If using PlanetScale (Recommended - Free)

1. Go to https://planetscale.com
2. Sign up and create a new MySQL database
3. Go to **Connect** → **Node.js** and copy the connection string
4. Create a new user with secure password in PlanetScale dashboard
5. Note your credentials:
   - Host: (from connection string)
   - User: (from connection string)
   - Password: (your secure password)
   - Database: `agrosmart`

### Initialize Database Schema

1. Connect to your MySQL database using any MySQL client
2. Run the SQL commands from `database/schema.sql` to create tables:
   ```sql
   -- Copy all SQL from database/schema.sql and run in your MySQL client
   ```

---

## Step 2: Set Up Environment Variables

### For Main Flask Backend

Create environment variables in Vercel for the Flask app:

```
DB_HOST=your-mysql-host.planetscale.com
DB_USER=your-username
DB_PASSWORD=your-secure-password
DB_NAME=agrosmart
SECRET_KEY=generate-a-random-string-here
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### For Drone Backend

```
PORT=3000
NODE_ENV=production
FRONTEND_URL=https://your-drone-frontend.vercel.app
DRONE_NAME=Agro-Scout-1
```

### For Drone Frontend

```
VITE_BACKEND_URL=https://your-drone-backend.vercel.app
VITE_APP_BACKEND_URL=https://your-flask-backend.vercel.app
VITE_DRONE_SERVER_URL=https://your-drone-backend.vercel.app
```

---

## Step 3: Deploy to Vercel

### Deploy Flask Backend

```bash
# Install Vercel CLI
npm install -g vercel

# In the AgroSmart root directory
cd /path/to/AgroSmart
vercel deploy --prod
```

Or link your GitHub repo and deploy from Vercel dashboard:
1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Select "AgroSmart" as the root directory
5. Add environment variables (from Step 2)
6. Deploy

### Deploy Drone Backend

```bash
cd drone-control-system/backend
vercel deploy --prod
```

### Deploy Drone Frontend

```bash
cd drone-control-system/frontend
vercel deploy --prod
```

---

## Step 4: Configure CORS and URLs

After deployment, you'll have URLs like:
- Flask Backend: `https://agrosmart.vercel.app`
- Drone Backend: `https://agrosmart-drone-backend.vercel.app`
- Drone Frontend: `https://agrosmart-drone-frontend.vercel.app`

Update the environment variables:
1. Update `FRONTEND_URL` in Drone Backend with your Drone Frontend URL
2. Update `VITE_BACKEND_URL` and `VITE_DRONE_SERVER_URL` in Drone Frontend with your Drone Backend URL

---

## Step 5: Verify Deployment

### Test Flask Backend
```bash
curl https://your-flask-backend.vercel.app/
# Should return the home page HTML
```

### Test Drone Backend
```bash
curl https://your-drone-backend.vercel.app/
# Should return JSON response
```

### Test Drone Frontend
```bash
# Open in browser: https://your-drone-frontend.vercel.app
# Should load the React dashboard
```

---

## Troubleshooting

### "Could not import app.py"
- Check that `wsgi.py` exists in the root directory
- Verify `requirements.txt` has all dependencies
- Check that `app.py` has no syntax errors

### "FUNCTION_INVOCATION_FAILED"
- Check application logs: `vercel logs <deployment-url>`
- Verify database connection credentials
- Check that MySQL database is accessible from Vercel

### "Module not found" errors
- Run `pip install -r requirements.txt` locally to verify
- Check Python version compatibility (3.11+ recommended)

### Database Connection Errors
- Verify `DB_HOST`, `DB_USER`, `DB_PASSWORD` in environment variables
- Test connection locally first
- Check database firewall allows Vercel IPs
- For PlanetScale: Ensure SSL is enabled

### Socket.io Connection Issues
- Check that both CORS origins are correctly configured
- Verify `FRONTEND_URL` in Drone Backend environment
- Check browser console for connection errors

### Static Files Not Loading
- Static files from Flask should work automatically
- For React app, check that `dist/` folder is being built

---

## Local Development

### Run Flask Backend Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with local credentials
# Copy from .env.example and set your local database

# Run Flask app
python app.py
# Or: flask run
```

### Run Drone Backend Locally
```bash
cd drone-control-system/backend
npm install
npm run dev
# Runs on http://localhost:4000
```

### Run Drone Frontend Locally
```bash
cd drone-control-system/frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

---

## File Reference

### Key Modified Files for Deployment

1. **`requirements.txt`** - Updated with all Python dependencies
2. **`wsgi.py`** - Created for Vercel compatibility
3. **`vercel.json`** - Created at root for Flask backend
4. **`app.py`** - Updated to support environment variables
5. **`drone-control-system/backend/vercel.json`** - Created
6. **`drone-control-system/frontend/vercel.json`** - Created
7. **`.env.example`** files - Updated with production settings

### No Changes Needed
- Database schema (`database/schema.sql`)
- HTML templates (`templates/`)
- Business logic (all route handlers)
- UI/UX design
- Android app

---

## Database Schema Setup

After connecting your database, run this in your MySQL client:

```sql
-- Copy the entire contents of database/schema.sql file
```

All tables will be created:
- `users` - User accounts and profiles
- `machinery` - Equipment/machinery listings
- `bookings` - Machinery booking records
- `crop_prices` - Market crop price data

---

## Production Checklist

- [ ] MySQL database created and schema initialized
- [ ] Environment variables set in Vercel for all 3 projects
- [ ] `SECRET_KEY` changed to a strong random value
- [ ] Database backups configured
- [ ] CORS URLs verified and updated
- [ ] SSL certificates auto-configured by Vercel
- [ ] Domain names configured (optional)
- [ ] Email service for OTP (if using email-based verification)
- [ ] Monitoring and logs checked

---

## Support

For issues with:
- **Vercel Deployment:** Check Vercel Dashboard → Deployments → Logs
- **Database:** Use your database provider's admin panel
- **CORS/Networking:** Check browser console → Network tab
- **Application:** Check Vercel function logs for error details

---

## Next Steps

1. Set up monitoring and error tracking (Sentry, LogRocket)
2. Configure backups for MySQL database
3. Set up CDN for static assets
4. Configure custom domain names
5. Add email service for notifications
6. Implement rate limiting for APIs

