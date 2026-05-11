import { io } from "socket.io-client";

let socket = null;
let telemetryCallback = null;

export const connectSocket = (backendUrl) => {
  if (socket) return socket;
  socket = io(backendUrl, { transports: ["websocket"], autoConnect: true });

  socket.on("connect", () => {
    console.log("Connected to drone backend", socket.id);
  });

  socket.on("telemetry", (state) => {
    if (telemetryCallback) telemetryCallback(state);
  });

  socket.on("disconnect", () => {
    console.log("Socket disconnected");
  });

  return socket;
};

export const subscribeTelemetry = (callback) => {
  telemetryCallback = callback;
  return () => {
    telemetryCallback = null;
  };
};

export const sendSocketCommand = (backendUrl, action, payload = {}) => {
  if (socket && socket.connected) {
    socket.emit("command", { action, payload });
    return;
  }

  fetch(`${backendUrl}/api/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, payload }),
  }).catch((error) => console.error("Command request failed", error));
};
