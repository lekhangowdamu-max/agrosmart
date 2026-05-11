import { motion } from "framer-motion";

const VideoPanel = ({ telemetry }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-3xl border border-slate-700/70 bg-slate-950/85 p-5 shadow-drone backdrop-blur-xl"
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-400/75">Camera feed</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Simulated drone stream</h3>
        </div>
        <span className="rounded-full bg-slate-800/70 px-3 py-1 text-xs uppercase tracking-[0.3em] text-slate-300">AI overlay</span>
      </div>

      <div className="relative overflow-hidden rounded-3xl bg-slate-900/95">
        <div className="aspect-[16/9] bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.25),_transparent_47%),radial-gradient(circle_at_bottom_right,_rgba(14,165,233,0.25),_transparent_36%),#020617]">
          <div className="absolute inset-0 animate-pulse bg-[linear-gradient(115deg,rgba(255,255,255,0.08),transparent_30%)]" />
          <div className="absolute left-5 top-5 h-14 w-28 rounded-3xl border border-emerald-300/60 bg-emerald-500/10 p-3 text-xs text-slate-100">
            <div className="mb-2 font-semibold">Live Feed</div>
            <div className="text-[11px] text-slate-300">Resolution 1280 x 720</div>
          </div>
          <div className="absolute right-5 top-5 rounded-3xl border border-white/10 bg-slate-950/80 px-3 py-2 text-xs uppercase tracking-[0.3em] text-slate-300">AI Detect</div>
          <div className="absolute left-8 top-28 h-16 w-32 rounded-2xl border border-fuchsia-500/70 bg-fuchsia-500/10 backdrop-blur-sm" />
          <div className="absolute right-10 top-44 h-20 w-40 rounded-2xl border border-amber-400/80 bg-amber-400/10 backdrop-blur-sm" />
          <div className="absolute left-1/2 top-56 h-14 w-28 -translate-x-1/2 rounded-2xl border border-cyan-300/70 bg-cyan-300/10 backdrop-blur-sm" />
        </div>
      </div>

      <div className="mt-5 grid gap-4 rounded-3xl bg-slate-900/80 p-4 text-sm text-slate-300 sm:grid-cols-3">
        <div>
          <p className="uppercase tracking-[0.25em] text-slate-500">Area scanned</p>
          <p className="mt-2 text-lg font-medium text-white">82.4 ha</p>
        </div>
        <div>
          <p className="uppercase tracking-[0.25em] text-slate-500">Detected targets</p>
          <p className="mt-2 text-lg font-medium text-white">4 zones</p>
        </div>
        <div>
          <p className="uppercase tracking-[0.25em] text-slate-500">AI overlay</p>
          <p className="mt-2 text-lg font-medium text-white">Enabled</p>
        </div>
      </div>
    </motion.div>
  );
};

export default VideoPanel;
