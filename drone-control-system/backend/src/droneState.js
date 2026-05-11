const createDroneState = () => ({
  id: "agro-drone-001",
  name: process.env.DRONE_NAME || "Agro Scout",
  status: "grounded",
  battery: 100,
  altitude: 0,
  speed: 0,
  latitude: 26.9124,
  longitude: 75.7873,
  heading: 0,
  signal: 100,
  mode: "idle",
  lastCommand: "none",
  waypoint: null,
  logs: [
    { time: new Date().toISOString(), event: "System initialized", level: "info" }
  ],
  commandQueue: []
});

const addLog = (state, event, level = "info") => {
  state.logs.unshift({ time: new Date().toISOString(), event, level });
  if (state.logs.length > 40) state.logs.pop();
};

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

const updateTelemetry = (state) => {
  // Simulate battery drain and signal fluctuation.
  if (state.status === "airborne") {
    state.battery = clamp(state.battery - 0.35, 0, 100);
    state.signal = clamp(state.signal + (Math.random() * 4 - 2), 22, 100);
  } else {
    state.signal = clamp(state.signal + (Math.random() * 2 - 1), 30, 100);
  }

  // Simulate natural drift when airborne.
  if (state.status === "airborne") {
    const drift = 0.00003;
    const headingRad = (state.heading * Math.PI) / 180;
    state.latitude += Math.cos(headingRad) * drift * (state.speed / 60);
    state.longitude += Math.sin(headingRad) * drift * (state.speed / 60);
    state.latitude = parseFloat(state.latitude.toFixed(6));
    state.longitude = parseFloat(state.longitude.toFixed(6));
  }

  if (state.waypoint) {
    const dx = state.waypoint.latitude - state.latitude;
    const dy = state.waypoint.longitude - state.longitude;
    const distance = Math.sqrt(dx * dx + dy * dy);
    if (distance < 0.00012) {
      addLog(state, "Waypoint reached", "success");
      state.waypoint = null;
      state.mode = "hover";
      state.speed = Math.max(state.speed - 12, 8);
    } else {
      state.heading = Math.round((Math.atan2(dy, dx) * 180) / Math.PI + 360) % 360;
      state.latitude += dx * 0.15;
      state.longitude += dy * 0.15;
      state.speed = clamp(state.speed + 2, 12, 55);
      state.mode = "navigation";
    }
  }

  if (state.battery <= 15 && state.status === "airborne") {
    state.mode = "returning";
    addLog(state, "Low battery: return to home recommended", "warning");
  }

  state.altitude = clamp(state.altitude + (state.status === "airborne" ? 0 : 0), 0, 500);
  if (state.status !== "airborne") {
    state.speed = 0;
  }
};

const executeCommand = (state, command) => {
  const action = command.action;
  const payload = command.payload || {};
  state.lastCommand = action;

  switch (action) {
    case "takeoff":
      if (state.status === "grounded") {
        state.status = "airborne";
        state.altitude = 60;
        state.speed = 25;
        state.mode = "takeoff";
        addLog(state, "Takeoff initiated", "info");
      }
      break;
    case "land":
      if (state.status === "airborne") {
        state.status = "landing";
        state.speed = 18;
        state.mode = "landing";
        addLog(state, "Landing sequence started", "info");
      }
      break;
    case "emergency":
      state.status = "emergency";
      state.speed = 0;
      state.altitude = clamp(state.altitude - 40, 0, 500);
      state.mode = "emergency stop";
      addLog(state, "EMERGENCY STOP activated", "error");
      break;
    case "move":
      if (state.status === "airborne") {
        const { direction } = payload;
        state.heading = ({ forward: 0, backward: 180, left: 270, right: 90 }[direction] || state.heading);
        state.speed = clamp(state.speed + 6, 10, 80);
        state.mode = "manual flight";
        addLog(state, `Manual move: ${direction}`, "info");
      }
      break;
    case "setAltitude":
      if (state.status === "airborne") {
        state.altitude = clamp(payload.altitude || state.altitude, 0, 500);
        addLog(state, `Altitude set to ${state.altitude}m`, "info");
      }
      break;
    case "setSpeed":
      if (state.status === "airborne") {
        state.speed = clamp(payload.speed || state.speed, 0, 100);
        addLog(state, `Speed adjusted to ${state.speed}%`, "info");
      }
      break;
    case "spray":
      state.mode = state.mode === "spray" ? "hover" : "spray";
      addLog(state, `Spray mode ${state.mode === "spray" ? "activated" : "deactivated"}`, "info");
      break;
    case "monitor":
      state.mode = "crop monitoring";
      addLog(state, "Crop monitoring started", "info");
      break;
    case "setWaypoint":
      if (payload.latitude && payload.longitude) {
        state.waypoint = { latitude: payload.latitude, longitude: payload.longitude };
        addLog(state, `New waypoint set (${payload.latitude.toFixed(5)}, ${payload.longitude.toFixed(5)})`, "info");
      }
      break;
    default:
      addLog(state, `Unknown command: ${action}`, "warning");
  }
};

module.exports = {
  createDroneState,
  updateTelemetry,
  executeCommand,
  addLog
};
