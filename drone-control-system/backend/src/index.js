require("dotenv").config();
const express = require("express");
const http = require("http");
const cors = require("cors");
const { Server } = require("socket.io");
const { createDroneState, updateTelemetry, executeCommand, addLog } = require("./droneState");

const app = express();
const server = http.createServer(app);
const port = Number(process.env.PORT || 4000);
const frontendOrigin = process.env.FRONTEND_URL || "http://localhost:5173";

const io = new Server(server, {
  cors: {
    origin: frontendOrigin,
    methods: ["GET", "POST"],
  },
});

app.use(cors({ origin: frontendOrigin }));
app.use(express.json());

const state = createDroneState();
let broadcasting = false;

const broadcastTelemetry = () => {
  updateTelemetry(state);

  if (state.status === "landing" && state.altitude > 0) {
    state.altitude = Math.max(state.altitude - 8, 0);
    state.speed = clamp(state.speed - 2, 0, 28);
    if (state.altitude === 0) {
      state.status = "grounded";
      state.mode = "idle";
      state.speed = 0;
      addLog(state, "Landing complete", "success");
    }
  }

  if (state.status === "emergency") {
    state.altitude = Math.max(state.altitude - 10, 0);
    if (state.altitude === 0) {
      state.status = "grounded";
      state.mode = "idle";
      addLog(state, "Emergency stop complete", "error");
    }
  }

  io.emit("telemetry", state);
};

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

app.get("/api/status", (req, res) => {
  res.json({ success: true, state });
});

app.get("/api/logs", (req, res) => {
  res.json({ success: true, logs: state.logs });
});

app.post("/api/command", async (req, res) => {
  const { action, payload } = req.body || {};
  if (!action) {
    return res.status(400).json({ success: false, message: "Missing action" });
  }

  const delay = 500 + Math.random() * 800;
  addLog(state, `Command received: ${action}`, "info");
  setTimeout(() => executeCommand(state, { action, payload }), delay);

  res.json({ success: true, message: `Command ${action} queued`, delay: Math.round(delay) });
});

io.on("connection", (socket) => {
  addLog(state, `Client connected (${socket.id})`, "info");
  socket.emit("telemetry", state);

  socket.on("command", ({ action, payload }) => {
    if (!action) return;
    const delay = 500 + Math.random() * 800;
    addLog(state, `Socket command received: ${action}`, "info");
    setTimeout(() => executeCommand(state, { action, payload }), delay);
  });

  socket.on("disconnect", () => {
    addLog(state, `Client disconnected (${socket.id})`, "warning");
  });
});

setInterval(() => {
  broadcastTelemetry();
}, 1000);

server.listen(port, () => {
  console.log(`Agro Drone backend running on http://localhost:${port}`);
});
