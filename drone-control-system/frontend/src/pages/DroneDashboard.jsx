import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import VideoPanel from "../components/VideoPanel";
import JoystickControl from "../components/JoystickControl";
import TelemetryPanel from "../components/TelemetryPanel";
import MapPanel from "../components/MapPanel";
import StatusLogs from "../components/StatusLogs";
import { connectSocket, sendSocketCommand, subscribeTelemetry } from "../services/socketService";

const backendUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:4000";

const DroneDashboard = ({ user, onLogout }) => {
  const [telemetry, setTelemetry] = useState(null);
  const [toast, setToast] = useState(null);
  const [activeControl, setActiveControl] = useState(null);

  useEffect(() => {
    connectSocket(backendUrl);
    const unsubscribe = subscribeTelemetry((state) => {
      setTelemetry(state);
    });
    return () => unsubscribe();
  }, []);

  const handleCommand = (action, payload = {}) => {
    setActiveControl(action);
    sendSocketCommand(backendUrl, action, payload);
    setToast({ message: `Command queued: ${action}`, variant: "info" });
    window.setTimeout(() => setActiveControl(null), 300);
    window.setTimeout(() => setToast(null), 2200);
  };

  const statusTag = useMemo(() => {
    if (!telemetry) return "Connecting...";
    return telemetry.status === "airborne" ? "In Flight" : telemetry.status === "grounded" ? "Grounded" : telemetry.status;
  }, [telemetry]);

  return (
    <div className="min-h-screen px-4 py-4 lg:px-6">
      <div className="mb-5 flex flex-col gap-4 rounded-3xl border border-slate-700/70 bg-slate-950/85 p-5 shadow-drone backdrop-blur-xl lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-400/75">Agro Drone Control System</p>
          <h2 className="mt-2 text-3xl font-semibold text-white">Welcome back, {user.name}</h2>
          <p className="mt-2 text-slate-400">Role: {user.role}. Monitor telemetry, set waypoints and manage drone operations.</p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="rounded-2xl bg-slate-900/80 px-4 py-3 text-sm text-slate-200">
            Status: <span className="font-semibold text-emerald-300">{statusTag}</span>
          </div>
          <button
            onClick={onLogout}
            className="inline-flex items-center justify-center rounded-2xl bg-slate-700 px-5 py-3 text-sm font-semibold text-slate-100 transition hover:bg-slate-600"
          >
            Logout
          </button>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <div className="space-y-4">
          <VideoPanel telemetry={telemetry} />

          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-3xl border border-slate-700/70 bg-slate-950/85 p-5 shadow-drone backdrop-blur-xl">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.35em] text-emerald-400/75">Drone commands</p>
                  <h3 className="mt-2 text-xl font-semibold text-white">Flight controls</h3>
                </div>
                <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs uppercase tracking-[0.3em] text-emerald-300">Real-time</span>
              </div>

              <JoystickControl onCommand={handleCommand} active={activeControl} />

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <button
                  onClick={() => handleCommand("takeoff")}
                  className="rounded-2xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-slate-950 shadow hover:bg-emerald-400"
                >
                  Takeoff
                </button>
                <button
                  onClick={() => handleCommand("land")}
                  className="rounded-2xl bg-slate-700 px-4 py-3 text-sm font-semibold text-slate-100 shadow hover:bg-slate-600"
                >
                  Land
                </button>
                <button
                  onClick={() => handleCommand("emergency")}
                  className="rounded-2xl bg-red-500 px-4 py-3 text-sm font-semibold text-white shadow hover:bg-red-400"
                >
                  Emergency Stop
                </button>
                <button
                  onClick={() => handleCommand("spray")}
                  className="rounded-2xl bg-cyan-500 px-4 py-3 text-sm font-semibold text-slate-950 shadow hover:bg-cyan-400"
                >
                  Spray Mode
                </button>
              </div>
            </div>

            <TelemetryPanel telemetry={telemetry} onSetAltitude={(value) => handleCommand("setAltitude", { altitude: value })} onSetSpeed={(value) => handleCommand("setSpeed", { speed: value })} />
          </div>

          <StatusLogs logs={telemetry?.logs || []} />
        </div>

        <MapPanel telemetry={telemetry} onWaypoint={(coords) => handleCommand("setWaypoint", coords)} />
      </div>

      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 12 }}
            className="fixed bottom-5 right-5 rounded-3xl bg-slate-950/95 px-5 py-4 text-sm text-slate-100 shadow-xl shadow-slate-900/40"
          >
            {toast.message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DroneDashboard;
