import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import StationDetails from "./pages/StationDetails";
import MapPage from "./pages/MapPage";

import Login from "./pages/Login";
import Register from "./pages/Register";

import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import Favorites from "./pages/Favorites";
import Sessions from "./pages/Sessions";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-[#f8fafc] text-slate-900 font-sans antialiased">
        <Navbar />

        <div className="flex-1 flex flex-col">
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/stations/:stationId" element={<StationDetails />} />
              <Route path="/map" element={<MapPage />} />
              <Route path="/favorites" element={<Favorites />} />
              <Route path="/sessions" element={<Sessions />} />
            </Route>
          </Routes>
        </div>

        {/* Global Product Footer */}
        <footer className="border-t border-slate-200 bg-white py-6 mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-800">⚡ EVConnect Platform</span>
              <span>— Intelligent Mobility & Charging Forecasts</span>
            </div>
            <div className="flex items-center gap-4 text-slate-400">
              <span>30-Min Prediction Horizon</span>
              <span>•</span>
              <span>Adaptive ML Network</span>
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
