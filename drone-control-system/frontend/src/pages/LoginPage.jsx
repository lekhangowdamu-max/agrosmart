import { motion } from "framer-motion";
import { useState } from "react";

const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("farmer");

  const handleSubmit = (event) => {
    event.preventDefault();
    const name = email.split("@")[0] || "Drone Pilot";
    onLogin({ name, email, role });
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-5xl items-center justify-center px-4 py-12">
      <motion.section
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full rounded-3xl border border-slate-700/70 bg-slate-950/90 p-8 shadow-drone backdrop-blur-xl"
      >
        <div className="mb-8 text-center">
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-400/75">Agro Drone Control</p>
          <h1 className="mt-4 text-4xl font-semibold text-white">Ground Control Login</h1>
          <p className="mt-3 text-slate-400">Sign in as farmer or admin to manage the crop monitoring drone.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-300">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="pilot@agrosmart.com"
              className="w-full rounded-2xl border border-slate-700 bg-slate-900/90 px-4 py-3 text-slate-100 outline-none transition focus:border-emerald-400"
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-300">Role</span>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full rounded-2xl border border-slate-700 bg-slate-900/90 px-4 py-3 text-slate-100 outline-none"
            >
              <option value="farmer">Farmer</option>
              <option value="admin">Admin</option>
            </select>
          </label>

          <button
            type="submit"
            className="w-full rounded-2xl bg-emerald-500 px-5 py-3 text-base font-semibold text-slate-950 shadow hover:bg-emerald-400"
          >
            Enter Control Hub
          </button>
        </form>
      </motion.section>
    </main>
  );
};

export default LoginPage;
