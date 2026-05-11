import { useEffect, useRef } from "react";
import nipplejs from "nipplejs";

const directions = {
  up: "forward",
  down: "backward",
  left: "left",
  right: "right",
};

const JoystickControl = ({ onCommand, active }) => {
  const joystickRef = useRef(null);

  useEffect(() => {
    if (!joystickRef.current) return;
    const manager = nipplejs.create({
      zone: joystickRef.current,
      mode: "static",
      position: { left: "50%", top: "50%" },
      color: "#34d399",
      size: 140,
    });

    manager.on("move", (evt, data) => {
      if (!data.direction) return;
      const dir = directions[data.direction.angle] || null;
      if (dir) onCommand("move", { direction: dir });
    });

    return () => manager.destroy();
  }, [onCommand]);

  return (
    <div className="rounded-3xl border border-slate-700/70 bg-slate-900/85 p-5 shadow-inner shadow-slate-950/40">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-400/75">Joystick</p>
          <h4 className="mt-1 text-lg font-semibold text-white">Virtual flight stick</h4>
        </div>
        <span className="rounded-full bg-slate-800/80 px-3 py-1 text-xs uppercase tracking-[0.3em] text-slate-300">Touch control</span>
      </div>
      <div className="relative flex h-[220px] items-center justify-center rounded-3xl bg-slate-950/90 p-6">
        <div className="absolute inset-0 rounded-3xl border border-slate-700/50 bg-gradient-to-br from-slate-950/10 via-transparent to-transparent" />
        <div
          ref={joystickRef}
          className="relative z-10 flex h-full w-full items-center justify-center rounded-3xl bg-slate-900/80"
        >
          <div className="pointer-events-none absolute h-24 w-24 rounded-full border border-slate-600/70 bg-slate-700/20" />
        </div>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-300">
        {Object.values(directions).map((dir) => (
          <div key={dir} className="rounded-2xl border border-slate-700/60 bg-slate-900/80 px-3 py-2">
            {dir.charAt(0).toUpperCase() + dir.slice(1)}
            {active === "move" && dir === "forward" ? " •" : ""}
          </div>
        ))}
      </div>
    </div>
  );
};

export default JoystickControl;
