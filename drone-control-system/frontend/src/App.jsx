import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import LoginPage from "./pages/LoginPage";
import DroneDashboard from "./pages/DroneDashboard";

const App = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const stored = window.localStorage.getItem("agro-drone-user");
    if (stored) setUser(JSON.parse(stored));
  }, []);

  const handleLogin = (profile) => {
    setUser(profile);
    window.localStorage.setItem("agro-drone-user", JSON.stringify(profile));
  };

  const handleLogout = () => {
    setUser(null);
    window.localStorage.removeItem("agro-drone-user");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-midnight via-slate-950 to-slate-900 text-slate-100">
      <AnimatePresence mode="wait">
        {!user ? (
          <motion.div
            key="login"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.35 }}
          >
            <LoginPage onLogin={handleLogin} />
          </motion.div>
        ) : (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.35 }}
          >
            <DroneDashboard user={user} onLogout={handleLogout} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default App;
