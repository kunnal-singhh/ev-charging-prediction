import { useEffect, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("dashboard");

  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("user");
    return savedUser ? JSON.parse(savedUser) : null;
  });

  // Track active section on scroll when on the home page
  useEffect(() => {
    if (location.pathname !== "/") {
      return;
    }

    const handleScroll = () => {
      const stationsEl = document.getElementById("stations");
      if (stationsEl) {
        const rect = stationsEl.getBoundingClientRect();
        if (rect.top <= 200) {
          setActiveSection("stations");
        } else {
          setActiveSection("dashboard");
        }
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();

    return () => window.removeEventListener("scroll", handleScroll);
  }, [location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setMobileMenuOpen(false);
    navigate("/login");
  };

  // Don't show navbar on authentication pages
  if (location.pathname === "/login" || location.pathname === "/register") {
    return null;
  }

  const navLinkClasses = ({ isActive }) =>
    `px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-150 ${
      isActive && location.pathname !== "/"
        ? "bg-slate-900 text-white shadow-xs font-semibold"
        : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
    }`;

  const mobileNavLinkClasses = ({ isActive }) =>
    `block px-4 py-2.5 text-base font-medium rounded-xl transition-colors ${
      isActive && location.pathname !== "/"
        ? "bg-slate-900 text-white font-semibold"
        : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
    }`;

  const isDashboardActive = location.pathname === "/" && activeSection === "dashboard";
  const isStationsActive =
    (location.pathname === "/" && activeSection === "stations") ||
    location.pathname.startsWith("/stations/");

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/95 backdrop-blur-md transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Brand logo */}
          <div className="flex items-center gap-8">
            <NavLink
              to="/"
              className="flex items-center gap-2.5 text-slate-950 no-underline group focus:outline-none"
              onClick={() => setMobileMenuOpen(false)}
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-xs shadow-emerald-500/20 group-hover:scale-105 transition-transform">
                <svg
                  className="w-5 h-5 fill-current"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-bold tracking-tight text-slate-900 leading-none">
                  EVConnect
                </span>
                <span className="text-[10px] font-semibold text-emerald-600 tracking-wider uppercase leading-tight mt-0.5">
                  Smart Charging
                </span>
              </div>
            </NavLink>

            {/* Desktop Navigation Links */}
            <nav className="hidden md:flex items-center gap-1">
              <NavLink
                to="/"
                end
                className={() =>
                  `px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-150 ${
                    isDashboardActive
                      ? "bg-slate-900 text-white shadow-xs font-semibold"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`
                }
              >
                Dashboard
              </NavLink>
              <a
                href="/#stations"
                onClick={(e) => {
                  if (location.pathname === "/") {
                    e.preventDefault();
                    document.getElementById("stations")?.scrollIntoView({ behavior: "smooth" });
                    setActiveSection("stations");
                  }
                }}
                className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-150 ${
                  isStationsActive
                    ? "bg-slate-900 text-white shadow-xs font-semibold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                Stations
              </a>
              <NavLink to="/map" className={navLinkClasses}>
                Map
              </NavLink>
              <NavLink to="/favorites" className={navLinkClasses}>
                Favorites
              </NavLink>
              <NavLink to="/sessions" className={navLinkClasses}>
                Sessions
              </NavLink>
            </nav>
          </div>

          {/* Desktop Right Side / User */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold ring-2 ring-emerald-500/20">
                    {user.name ? user.name.charAt(0).toUpperCase() : "U"}
                  </div>
                  <span className="text-sm font-semibold text-slate-800 max-w-[130px] truncate">
                    {user.name}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center justify-center rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 shadow-xs hover:bg-slate-50 hover:text-slate-900 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400"
                >
                  Logout
                </button>
              </div>
            ) : (
              <NavLink
                to="/login"
                className="inline-flex items-center justify-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-xs hover:bg-slate-800 transition-colors"
              >
                Sign in
              </NavLink>
            )}
          </div>

          {/* Mobile Hamburger Button */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center rounded-lg p-2 text-slate-600 hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? (
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="2"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="2"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1 shadow-lg animate-in fade-in slide-in-from-top-2 duration-200">
          <NavLink
            to="/"
            end
            className={() =>
              `block px-4 py-2.5 text-base font-medium rounded-xl transition-colors ${
                isDashboardActive
                  ? "bg-slate-900 text-white font-semibold"
                  : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
              }`
            }
            onClick={() => setMobileMenuOpen(false)}
          >
            Dashboard
          </NavLink>
          <a
            href="/#stations"
            className={`block px-4 py-2.5 text-base font-medium rounded-xl transition-colors ${
              isStationsActive
                ? "bg-slate-900 text-white font-semibold"
                : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
            }`}
            onClick={(e) => {
              setMobileMenuOpen(false);
              if (location.pathname === "/") {
                e.preventDefault();
                document.getElementById("stations")?.scrollIntoView({ behavior: "smooth" });
                setActiveSection("stations");
              }
            }}
          >
            Stations
          </a>
          <NavLink
            to="/map"
            className={mobileNavLinkClasses}
            onClick={() => setMobileMenuOpen(false)}
          >
            Map
          </NavLink>
          <NavLink
            to="/favorites"
            className={mobileNavLinkClasses}
            onClick={() => setMobileMenuOpen(false)}
          >
            Favorites
          </NavLink>
          <NavLink
            to="/sessions"
            className={mobileNavLinkClasses}
            onClick={() => setMobileMenuOpen(false)}
          >
            Sessions
          </NavLink>

          <div className="pt-3 mt-2 border-t border-slate-100 flex items-center justify-between">
            {user ? (
              <>
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
                    {user.name ? user.name.charAt(0).toUpperCase() : "U"}
                  </div>
                  <span className="text-sm font-semibold text-slate-800">{user.name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Logout
                </button>
              </>
            ) : (
              <NavLink
                to="/login"
                className="w-full text-center block rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-xs"
                onClick={() => setMobileMenuOpen(false)}
              >
                Sign in
              </NavLink>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
