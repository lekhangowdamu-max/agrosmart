# Agro Drone Control Backend

This backend simulates a drone ground control station using Express and Socket.io.

## Install

  cd drone-control-system/backend
  npm install

## Run

  npm run dev

## API

- `GET /api/status` — current drone state
- `GET /api/logs` — historic status logs
- `POST /api/command` — send commands: `takeoff`, `land`, `emergency`, `move`, `setAltitude`, `setSpeed`, `spray`, `monitor`, `setWaypoint`

The server also broadcasts telemetry every second over Socket.io.
