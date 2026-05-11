import { motion } from "framer-motion";

const TelemetryPanel = ({ telemetry, onSetAltitude, onSetSpeed }) => {
  const batteryLevel = telemetry?.battery ?? 0;
  const batteryColor = batteryLevel > 60 ? "bg-emerald-400" : batteryLevel > 25 ? "bg-amber-400" : "bg-red-500";

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-3xl border border-slate-700/70 bg-slate-950/85 p-5 shadow-drone backdrop-blur-xl"
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-400/75">Telemetry</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Live drone status</h3>
        </div>
        <span className="rounded-full bg-slate-800/70 px-3 py-1 text-xs uppercase tracking-[0.3em] text-slate-300">Simulated</span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-3xl bg-slate-900/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Battery</p>
          <p className="mt-2 text-4xl font-bold text-white">{batteryLevel.toFixed(0)}%</p>
          <div className="mt-3 h-3 rounded-full bg-slate-800">
            <div className={`h-full rounded-full ${batteryColor}`} style={{ width: `${batteryLevel}%` }} />
          </div>
        </div>

        <div className="rounded-3xl bg-slate-900/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Signal</p>
          <p className="mt-2 text-4xl font-bold text-white">{telemetry?.signal ?? 0}%</p>
          <p className="mt-2 text-sm text-slate-400">GPS quality and link strength</p>
        </div>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div className="rounded-3xl bg-slate-900/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Altitude</p>
          <p className="mt-2 text-3xl font-semibold text-white">{telemetry?.altitude ?? 0} m</p>
          <input
            type="range"
            min="0"
            max="500"
            value={telemetry?.altitude ?? 0}
            onChange={(e) => onSetAltitude(Number(e.target.value))}
            className="mt-4 w-full accent-emerald-400"
          />
        </div>

        <div className="rounded-3xl bg-slate-900/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Speed</p>
          <p className="mt-2 text-3xl font-semibold text-white">{telemetry?.speed ?? 0}%</p>
          <input
            type="range"
            min="0"
            max="100"
            value={telemetry?.speed ?? 0}
            onChange={(e) => onSetSpeed(Number(e.target.value))}
            className="mt-4 w-full accent-cyan-400"
          />
        </div>
      </div>

      <div className="mt-5 grid gap-4 rounded-3xl bg-slate-900/80 p-4 text-sm text-slate-300 sm:grid-cols-2">
        <div>
          <p className="uppercase tracking-[0.25em] text-slate-500">Latitude</p>
          <p className="mt-2 text-lg font-medium text-white">{telemetry?.latitude?.toFixed(6) ?? "---"}</p>
        </div>
        <div>
          <p className="uppercase tracking-[0.25em] text-slate-500">Longitude</p>
          <p className="mt-2 text-lg font-medium text-white">{telemetry?.longitude?.toFixed(6) ?? "---"}</p>
        </div>
        <div>
          <p className="uppercase tracking-[0.25em] text-slate-500">Mode</p>
          <p className="mt-2 text-lg font-medium text-white">{telemetry?.mode ?? "idle"}</p>
        </div>
        <div>
          <p className="uppercase tracking-[0.25em] text-slate-500">Last command</p>
          <p className="mt-2 text-lg font-medium text-white">{telemetry?.lastCommand ?? "none"}</p>
        </div>
      </div>
    </motion.div>
  );
};

export default TelemetryPanel;
