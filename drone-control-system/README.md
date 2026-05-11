# Agro Drone Control System

A production-ready simulation of a smart farming drone ground station.
It includes a full-stack Node.js backend with WebSockets and a React + Vite frontend with Tailwind CSS, Framer Motion, and Leaflet map integration.

## Setup

### Backend

  cd drone-control-system/backend
  npm install
  cp .env.example .env
  npm run dev

The backend runs at `http://localhost:4000` by default.

### Frontend

  cd drone-control-system/frontend
  npm install
  cp .env.example .env
  npm run dev

The frontend runs at `http://localhost:5173` by default and connects to the backend via `VITE_BACKEND_URL`.

## Features

- Real-time telemetry updates via Socket.io
- Virtual joystick flight controls using nipplejs
- Altitude and speed sliders
- Leaflet map with live drone position and waypoint selection
- Simulated battery drain, command delay, and warning alerts
- AI-mode UI overlays and status logs
- Farmer/admin login page

## Available commands

- `takeoff`
- `land`
- `emergency`
- `move`
- `setAltitude`
- `setSpeed`
- `spray`
- `monitor`
- `setWaypoint`

If you want the dashboard to connect to a different backend, set `VITE_BACKEND_URL` in `frontend/.env`.
