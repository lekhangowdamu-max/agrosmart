import { motion } from "framer-motion";

const StatusLogs = ({ logs }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-3xl border border-slate-700/70 bg-slate-950/85 p-5 shadow-drone backdrop-blur-xl"
    >
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-400/75">Logs</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Drone event history</h3>
        </div>
        <span className="rounded-full bg-slate-800/70 px-3 py-1 text-xs uppercase tracking-[0.3em] text-slate-300">Latest</span>
      </div>

      <div className="space-y-3 overflow-hidden rounded-3xl bg-slate-900/80 p-4">
        {logs.slice(0, 6).map((entry, index) => (
          <div key={`${entry.time}-${index}`} className="rounded-2xl border border-slate-700/60 bg-slate-950/90 p-3">
            <div className="flex items-center justify-between gap-3 text-xs uppercase tracking-[0.25em] text-slate-400">
              <span>{new Date(entry.time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
              <span className={entry.level === "error" ? "text-red-400" : entry.level === "warning" ? "text-amber-300" : "text-emerald-300"}>{entry.level}</span>
            </div>
            <p className="mt-2 text-sm text-slate-100">{entry.event}</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default StatusLogs;
