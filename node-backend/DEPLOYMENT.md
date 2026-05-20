# Deployment Guide

Complete guide for deploying AgroSmart Node.js backend to various platforms.

## Pre-Deployment Checklist

- [ ] All tests pass (`npm test`)
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] SSL certificate ready (for production)
- [ ] Domain name set up
- [ ] Backups created
- [ ] Monitoring configured
- [ ] Logs setup verified

## 1. Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI installed
- Git repository initialized

### Steps

```bash
# 1. Login to Heroku
heroku login

# 2. Create Heroku app
heroku create agrosmart-backend

# 3. Add MySQL database (JawsDB addon)
heroku addons:create jawsdb:kitefin

# 4. Set environment variables
heroku config:set NODE_ENV=production
heroku config:set SESSION_SECRET=$(openssl rand -hex 32)
heroku config:set SECRET_KEY=$(openssl rand -hex 32)

# 5. Deploy
git push heroku main

# 6. View logs
heroku logs --tail
```

### Procfile

Create `Procfile` in root:
```
web: node server.js
```

### package.json

Add engines section:
```json
{
  "engines": {
    "node": "16.x",
    "npm": "8.x"
  }
}
```

## 2. Vercel Deployment

### Prerequisites
- Vercel account
- Vercel CLI installed

### Steps

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
vercel --prod

# 3. Follow prompts to configure
```

### vercel.json

Create `vercel.json` in root:
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

## 3. AWS EC2 Deployment

### Prerequisites
- AWS account
- EC2 instance running Ubuntu 20.04
- Security group configured

### Steps

```bash
# 1. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 2. Update system
sudo apt update && sudo apt upgrade -y

# 3. Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# 4. Install MySQL
sudo apt-get install -y mysql-server

# 5. Clone repository
git clone your-repo.git
cd node-backend

# 6. Install dependencies
npm ci --only=production

# 7. Create .env
nano .env
# Add configuration

# 8. Setup database
mysql -u root -p < database_schema.sql

# 9. Start with PM2 (process manager)
sudo npm i -g pm2
pm2 start server.js --name "agrosmart"
pm2 startup
pm2 save
```

### Nginx Reverse Proxy

Configure Nginx to proxy requests:

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create config
sudo nano /etc/nginx/sites-available/agrosmart
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/agrosmart /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## 4. Docker Deployment

### Dockerfile

```dockerfile
FROM node:16-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy app
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Start app
CMD ["node", "server.js"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database_schema.sql:/docker-entrypoint-initdb.d/schema.sql

  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DB_HOST: mysql
      DB_USER: root
      DB_PASSWORD: ${DB_PASSWORD}
      DB_NAME: ${DB_NAME}
      NODE_ENV: production
      SESSION_SECRET: ${SESSION_SECRET}
    depends_on:
      - mysql
    volumes:
      - ./:/app
      - /app/node_modules

volumes:
  mysql_data:
```

Build and run:
```bash
docker-compose up -d
```

## 5. DigitalOcean Deployment

### App Platform

1. Connect GitHub repository
2. Click "New App"
3. Select repository
4. Configure build command: `npm ci`
5. Configure start command: `npm start`
6. Add environment variables
7. Set up database (DigitalOcean MySQL)
8. Deploy

### Droplet (Manual)

Similar to AWS EC2 steps above.

## 6. Azure Deployment

### App Service

```bash
# 1. Login
az login

# 2. Create resource group
az group create --name agrosmart --location eastus

# 3. Create app service plan
az appservice plan create --name agrosmart-plan --resource-group agrosmart --sku B1 --is-linux

# 4. Create web app
az webapp create --resource-group agrosmart --plan agrosmart-plan --name agrosmart-api --runtime "node|16"

# 5. Deploy
az webapp deployment source config-zip --resource-group agrosmart --name agrosmart-api --src app.zip
```

## 7. Google Cloud Deployment

### Cloud Run

```bash
# 1. Build container
gcloud builds submit --tag gcr.io/PROJECT-ID/agrosmart

# 2. Deploy to Cloud Run
gcloud run deploy agrosmart --image gcr.io/PROJECT-ID/agrosmart --platform managed --region us-central1 --set-env-vars DB_HOST=...
```

### Compute Engine

Similar to AWS EC2 / DigitalOcean Droplet.

## Production Configuration

### .env for Production

```env
NODE_ENV=production
PORT=3000
DB_HOST=your-db-host
DB_PORT=3306
DB_USER=agrosmart_user
DB_PASSWORD=strong_random_password
DB_NAME=agrosmart
SESSION_SECRET=strong_random_secret_key
SECRET_KEY=strong_random_key
SESSION_COOKIE_SECURE=true
CORS_ORIGIN=https://yourdomain.com
DB_POOL_SIZE=20
```

### Monitoring & Logging

#### Winston Logger Setup

```bash
npm install winston
```

Update `server.js`:
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Use logger
logger.info('Server started');
```

#### Sentry Error Tracking

```bash
npm install @sentry/node
```

```javascript
const Sentry = require("@sentry/node");

Sentry.init({ dsn: process.env.SENTRY_DSN });
app.use(Sentry.Handlers.errorHandler());
```

### Database Backups

#### Automated MySQL Backups

Create backup script `backup-db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/backup_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete
```

Schedule with cron:
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup-db.sh
```

## Performance Optimization

### Enable Caching

```javascript
app.use((req, res, next) => {
  res.set('Cache-Control', 'public, max-age=300');
  next();
});
```

### Enable Compression

```bash
npm install compression
```

```javascript
const compression = require('compression');
app.use(compression());
```

### Database Connection Pooling

Already configured in `config/database.js`:
```javascript
connectionLimit: 20  // Increase for production
```

## Monitoring & Alerting

### PM2 Monitoring

```bash
# Install PM2+
pm2 install pm2-auto-pull
pm2 monitoring
```

### Health Check Endpoint

Already available at: `/health`

Set up monitoring tool to ping this endpoint periodically.

## Rollback Plan

```bash
# Keep previous versions
git tag v1.0.0
git push origin v1.0.0

# Rollback if needed
git checkout v1.0.0
npm install
npm start
```

## Troubleshooting Deployment

### "Cannot find module"
```bash
rm -rf node_modules package-lock.json
npm install
```

### "Database connection refused"
- Verify DB credentials in .env
- Check database server is running
- Verify network access/firewall

### "Port already in use"
```bash
# Find process on port 3000
lsof -i :3000
kill -9 <PID>
```

### "Out of memory"
- Increase server RAM
- Enable memory monitoring
- Optimize database queries

## Performance Metrics

### Recommended Server Specs

| Users | CPU | RAM | DB |
|-------|-----|-----|-----|
| 100 | 1 CPU | 1 GB | 10 GB |
| 1000 | 2 CPU | 2 GB | 50 GB |
| 10K | 4 CPU | 4 GB | 100 GB |
| 100K | 8+ CPU | 8+ GB | 500+ GB |

## Security Hardening

- [ ] Enable HTTPS only
- [ ] Set strong passwords
- [ ] Enable database encryption
- [ ] Regular security updates
- [ ] Firewall configuration
- [ ] DDoS protection
- [ ] Regular backups
- [ ] Log monitoring

---

**Deployment Guide Complete!**

For platform-specific support, refer to:
- Heroku: https://devcenter.heroku.com/
- Vercel: https://vercel.com/docs
- AWS: https://docs.aws.amazon.com/
- Docker: https://docs.docker.com/
- Google Cloud: https://cloud.google.com/docs
