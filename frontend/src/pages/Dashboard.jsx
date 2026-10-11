import { useEffect, useMemo, useState } from "react";
import { getStationPredictions } from "../services/stationApi";
import StationCard from "../components/StationCard";
import RecommendedStations from "../components/RecommendedStations";
import StatCard from "../components/StatCard";
import { StationCardSkeleton, StatCardSkeleton } from "../components/LoadingSkeleton";

export default function Dashboard() {
  const [stations, setStations] = useState([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [predictionTimestamp, setPredictionTimestamp] = useState(null);

  /*
   * Initial load - calls API without hardcoded timestamp so backend provides latest dataset timestamp
   */
  useEffect(() => {
    let cancelled = false;

    const loadInitialStations = async () => {
      try {
        const result = await getStationPredictions();

        if (cancelled) return;

        setStations(result.stations || []);
        setPredictionTimestamp(result.timestamp || null);
      } catch (err) {
        if (cancelled) return;
        console.error("Dashboard prediction error:", err);
        setError(err.message || "Unable to load charging stations.");
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadInitialStations();

    return () => {
      cancelled = true;
    };
  }, []);

  /*
   * Refresh station predictions
   */
  const handleRefresh = async () => {
    try {
      setLoading(true);
      setError("");

      const result = await getStationPredictions();

      setStations(result.stations || []);
      setPredictionTimestamp(result.timestamp || null);
    } catch (err) {
      console.error("Dashboard prediction error:", err);
      setError(err.message || "Unable to load charging stations.");
    } finally {
      setLoading(false);
    }
  };

  /*
   * Search + filter
   */
  const filteredStations = useMemo(() => {
    const searchText = search.toLowerCase().trim();

    return stations.filter((station) => {
      const stationId = String(station.stationId || "").toLowerCase();
      const stationName = String(station.name || "").toLowerCase();

      const matchesSearch =
        stationId.includes(searchText) || stationName.includes(searchText);

      const matchesFilter =
        filter === "all" ||
        (filter === "available" && station.status === "available") ||
        (filter === "occupied" && station.status === "occupied");

      return matchesSearch && matchesFilter;
    });
  }, [stations, search, filter]);

  /*
   * Summary counts
   */
  const availableCount = stations.filter(
    (station) => station.status === "available"
  ).length;

  const occupiedCount = stations.filter(
    (station) => station.status === "occupied"
  ).length;

  /*
   * Handle hash navigation (e.g. /#stations)
   */
  useEffect(() => {
    if (window.location.hash === "#stations") {
      const el = document.getElementById("stations");
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [stations]);

  return (
    <main className="flex-1 bg-[#f8fafc] py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* ================================= */}
        {/* HERO SECTION */}
        {/* ================================= */}
        <section className="relative overflow-hidden rounded-3xl bg-slate-900 px-6 py-8 sm:px-10 sm:py-10 text-white shadow-xl shadow-slate-900/10">
          <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 right-1/4 -mb-10 w-64 h-64 bg-teal-500/10 rounded-full blur-2xl pointer-events-none" />

          <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div className="max-w-2xl space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/80 text-emerald-400 text-xs font-semibold tracking-wide uppercase">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Real-time ML Network
              </div>
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
                Find your next charge.
              </h1>
              <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
                Smart predictions to help you find the right charging station quickly with intelligent 30-minute horizon forecasting.
              </p>

              {predictionTimestamp && (
                <div className="flex items-center gap-2 pt-2 text-xs text-slate-400 font-mono">
                  <svg className="w-3.5 h-3.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Dataset timestamp: {new Date(predictionTimestamp).toLocaleString()}</span>
                </div>
              )}
            </div>

            {/* Refresh Button */}
            <div className="flex shrink-0">
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-500 px-5 py-3 text-sm font-bold text-slate-950 shadow-md shadow-emerald-500/20 hover:bg-emerald-400 hover:shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-60 disabled:cursor-wait active:scale-95"
              >
                <svg
                  className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2.5"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                <span>{loading ? "Refreshing..." : "Refresh predictions"}</span>
              </button>
            </div>
          </div>
        </section>

        {/* Global Error Banner if refresh fails with existing data */}
        {error && stations.length > 0 && (
          <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 flex items-center justify-between shadow-xs">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-rose-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
            <button
              onClick={handleRefresh}
              className="text-xs font-bold underline hover:no-underline"
            >
              Retry
            </button>
          </div>
        )}

        {/* ================================= */}
        {/* COMPACT STATS */}
        {/* ================================= */}
        <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {loading && stations.length === 0 ? (
            <>
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
            </>
          ) : (
            <>
              <StatCard
                title="Total Stations"
                value={stations.length}
                subtitle="Monitored in network"
                variant="default"
                icon={
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                }
              />
              <StatCard
                title="Available Now"
                value={availableCount}
                subtitle={`${stations.length ? ((availableCount / stations.length) * 100).toFixed(0) : 0}% network ready`}
                variant="success"
                icon={
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                }
              />
              <StatCard
                title="Occupied"
                value={occupiedCount}
                subtitle="Active charging"
                variant="danger"
                icon={
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                }
              />
            </>
          )}
        </section>

        {/* ================================= */}
        {/* SMART RECOMMENDATIONS */}
        {/* ================================= */}
        {!loading && stations.length > 0 && (
          <RecommendedStations stations={stations} />
        )}

        {/* ================================= */}
        {/* SEARCH AND FILTERS */}
        {/* ================================= */}
        <section id="stations" className="scroll-mt-20 space-y-4">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            {/* Search Input */}
            <div className="relative flex-1 max-w-md">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                <svg className="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search station name or ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder-slate-400 shadow-xs focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              />
              {search && (
                <button
                  onClick={() => setSearch("")}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-xs text-slate-400 hover:text-slate-600"
                >
                  Clear
                </button>
              )}
            </div>

            {/* Filter Dropdown */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="appearance-none rounded-xl border border-slate-200 bg-white py-2.5 pl-4 pr-9 text-sm font-semibold text-slate-700 shadow-xs hover:border-slate-300 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900/10 cursor-pointer"
                >
                  <option value="all">All Stations</option>
                  <option value="available">Available Now</option>
                  <option value="occupied">Occupied Now</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400">
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Result Count and active filters */}
          <div className="flex items-center justify-between text-xs text-slate-500 px-1">
            <span>
              Showing <strong className="text-slate-800 font-mono">{filteredStations.length}</strong> of{" "}
              <strong className="text-slate-800 font-mono">{stations.length}</strong> stations
            </span>
            {search && (
              <span className="text-slate-400">
                Filtered by &quot;{search}&quot;
              </span>
            )}
          </div>
        </section>

        {/* ================================= */}
        {/* STATION CARDS GRID */}
        {/* ================================= */}
        {loading && stations.length === 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {Array.from({ length: 8 }).map((_, index) => (
              <StationCardSkeleton key={index} />
            ))}
          </div>
        ) : error && stations.length === 0 ? (
          <div className="rounded-3xl border border-rose-200 bg-white p-12 text-center shadow-xs max-w-lg mx-auto space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">Something went wrong</h3>
              <p className="text-sm text-slate-500 mt-1">{error}</p>
            </div>
            <button
              onClick={handleRefresh}
              className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-slate-800 transition-colors"
            >
              Try again
            </button>
          </div>
        ) : filteredStations.length === 0 ? (
          <div className="rounded-3xl border border-slate-200 bg-white p-12 text-center shadow-xs max-w-lg mx-auto space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-slate-900">No stations found</h3>
            <p className="text-sm text-slate-500">
              We couldn&apos;t find any charging stations matching your current search or filter criteria.
            </p>
            <button
              onClick={() => {
                setSearch("");
                setFilter("all");
              }}
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              Reset filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {filteredStations.map((station) => (
              <StationCard key={station.stationId} station={station} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
