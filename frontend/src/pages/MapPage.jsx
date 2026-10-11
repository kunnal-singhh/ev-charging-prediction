import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getStationPredictions } from "../services/stationApi";
import StatusBadge from "../components/StatusBadge";

export default function MapPage() {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    const fetchStations = async () => {
      try {
        setLoading(true);
        // Call without hardcoded timestamp to use latest backend timestamp
        const result = await getStationPredictions();

        if (!cancelled) {
          setStations(result.stations || []);
          setLoading(false);
        }
      } catch (err) {
        console.error(err);
        if (!cancelled) {
          setError("Unable to load station data.");
          setLoading(false);
        }
      }
    };

    fetchStations();

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <main className="flex-1 bg-[#f8fafc] py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto space-y-6">
          <div className="h-8 w-48 rounded skeleton-shimmer" />
          <div className="h-4 w-72 rounded skeleton-shimmer" />
          <div className="h-48 rounded-3xl bg-white border border-slate-200 skeleton-shimmer" />
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex-1 bg-[#f8fafc] py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md mx-auto rounded-3xl border border-rose-200 bg-white p-8 text-center shadow-xs space-y-3">
          <h2 className="text-lg font-bold text-slate-900">Map unavailable</h2>
          <p className="text-sm text-rose-600">{error}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex-1 bg-[#f8fafc] py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Charging Station Map
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              {stations.length} charging stations monitored across network nodes.
            </p>
          </div>

          <Link
            to="/"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-slate-800 self-start sm:self-auto"
          >
            <span>View Dashboard</span>
          </Link>
        </div>

        {/* Location Coordinates Notice Card */}
        <section className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-xs space-y-4">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-50 text-teal-600">
            <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>

          <div className="max-w-xl mx-auto space-y-2">
            <h2 className="text-xl font-bold text-slate-900">
              Coordinate Mapping Notice
            </h2>
            <p className="text-sm text-slate-600 leading-relaxed">
              The current ACN dataset provides station identifiers, site identifiers, and charging-space identifiers. Station records are grouped by topological space rather than GPS coordinates.
            </p>
            <p className="text-xs text-slate-400">
              Interactive map pins will render automatically once verified geospatial coordinates are synchronized.
            </p>
          </div>
        </section>

        {/* Stations Directory List */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900">
              Network Station Directory
            </h2>
            <span className="text-xs font-mono text-slate-500">
              {stations.length} records
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {stations.map((station) => (
              <Link
                key={station.stationId}
                to={`/stations/${station.stationId}`}
                className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-xs hover:border-slate-300 hover:shadow-xs transition-all group"
              >
                <div className="min-w-0 flex-1 pr-2">
                  <strong className="text-sm font-bold text-slate-900 block truncate group-hover:text-emerald-600 transition-colors">
                    {station.name}
                  </strong>
                  <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-500 font-mono">
                    <span>{station.stationId}</span>
                    {station.spaceId && (
                      <span className="text-slate-400">Space {station.spaceId}</span>
                    )}
                  </div>
                </div>
                <StatusBadge status={station.status} size="sm" />
              </Link>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}