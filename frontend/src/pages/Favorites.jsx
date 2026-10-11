import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getFavorites, removeFavorite } from "../services/favoriteApi";
import { getStationPrediction } from "../services/stationApi";
import StatusBadge from "../components/StatusBadge";
import PredictionBar from "../components/PredictionBar";

export default function Favorites() {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    const loadFavorites = async () => {
      try {
        setLoading(true);
        const favoriteResult = await getFavorites();

        // Query each favorite station with the latest dataset prediction from backend
        const results = await Promise.all(
          (favoriteResult.favorites || []).map(async (stationId) => {
            try {
              return await getStationPrediction(stationId);
            } catch {
              return null;
            }
          })
        );

        if (!cancelled) {
          setStations(results.filter(Boolean));
          setLoading(false);
        }
      } catch (err) {
        console.error(err);
        if (!cancelled) {
          setError(err.message || "Unable to load favorites");
          setLoading(false);
        }
      }
    };

    loadFavorites();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleRemove = async (stationId) => {
    try {
      await removeFavorite(stationId);
      setStations((currentStations) =>
        currentStations.filter((station) => station.stationId !== stationId)
      );
    } catch (err) {
      console.error(err);
      alert(err.message || "Failed to remove station");
    }
  };

  if (loading) {
    return (
      <main className="flex-1 bg-[#f8fafc] py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="h-8 w-48 rounded skeleton-shimmer" />
          <div className="h-4 w-72 rounded skeleton-shimmer" />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 pt-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-48 rounded-2xl bg-white p-5 border border-slate-200 skeleton-shimmer" />
            ))}
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex-1 bg-[#f8fafc] py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md mx-auto rounded-3xl border border-rose-200 bg-white p-8 text-center shadow-xs space-y-3">
          <h2 className="text-lg font-bold text-slate-900">Unable to load favorites</h2>
          <p className="text-sm text-rose-600">{error}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex-1 bg-[#f8fafc] py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              My Favorite Stations
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Quick access to your saved charging points and their live predictions.
            </p>
          </div>

          <Link
            to="/"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-slate-800 self-start sm:self-auto"
          >
            <span>Browse stations</span>
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

        {/* Stations Grid */}
        {stations.length === 0 ? (
          <div className="rounded-3xl border border-slate-200 bg-white p-12 text-center shadow-xs max-w-lg mx-auto space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-500 flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
              </svg>
            </div>
            <h2 className="text-lg font-bold text-slate-900">No favorite stations</h2>
            <p className="text-sm text-slate-500">
              Save charging stations with the star icon on the dashboard to access them quickly here.
            </p>
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-slate-800 mt-2"
            >
              Explore stations →
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {stations.map((station) => {
              const pred = station.prediction || {};
              const avail = (Number(pred.availabilityProbability || 0) * 100).toFixed(1);
              const occ = (Number(pred.occupancyProbability || 0) * 100).toFixed(1);

              return (
                <div
                  key={station.stationId}
                  className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-xs hover:border-slate-300 hover:shadow-md transition-all space-y-4"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="text-base font-bold text-slate-900">
                          {station.name}
                        </h3>
                        <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                          <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">
                            {station.stationId}
                          </span>
                        </div>
                      </div>
                      <StatusBadge status={pred.status || "available"} size="sm" />
                    </div>

                    <div className="mt-4 space-y-2.5 pt-3 border-t border-slate-100">
                      <PredictionBar
                        label="Availability"
                        value={avail}
                        type="availability"
                        size="sm"
                      />
                      <PredictionBar
                        label="Occupancy"
                        value={occ}
                        type="occupancy"
                        size="sm"
                      />
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                    <button
                      onClick={() => handleRemove(station.stationId)}
                      className="text-xs font-semibold text-rose-600 hover:text-rose-700 p-1.5 rounded-lg hover:bg-rose-50 transition-colors"
                    >
                      Remove
                    </button>

                    <Link
                      to={`/stations/${station.stationId}`}
                      className="inline-flex items-center gap-1 rounded-xl bg-slate-900 px-3 py-1.5 text-xs font-bold text-white shadow-xs hover:bg-slate-800"
                    >
                      <span>Details</span>
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}