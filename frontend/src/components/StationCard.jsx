import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { addFavorite, getFavorites, removeFavorite } from "../services/favoriteApi";
import StatusBadge from "./StatusBadge";
import PredictionBar from "./PredictionBar";

export default function StationCard({ station }) {
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);

  const occupancy = station.occupancyProbability !== null && station.occupancyProbability !== undefined
    ? Number(station.occupancyProbability) * 100
    : 0;

  const availability = station.availabilityProbability !== null && station.availabilityProbability !== undefined
    ? Number(station.availabilityProbability) * 100
    : 0;

  const recommendationScore = station.recommendationScore !== undefined && station.recommendationScore !== null
    ? Number(station.recommendationScore).toFixed(1)
    : null;

  /*
   * Check whether this station is already saved by the logged-in user.
   */
  useEffect(() => {
    let cancelled = false;

    const checkFavorite = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const result = await getFavorites();
        if (!cancelled && result?.favorites) {
          setIsFavorite(result.favorites.includes(station.stationId));
        }
      } catch (error) {
        console.error("Failed to check favorite:", error);
      }
    };

    checkFavorite();

    return () => {
      cancelled = true;
    };
  }, [station.stationId]);

  const handleFavorite = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please login to save favorite stations.");
      return;
    }

    try {
      setFavoriteLoading(true);

      if (isFavorite) {
        await removeFavorite(station.stationId);
        setIsFavorite(false);
      } else {
        await addFavorite(station.stationId);
        setIsFavorite(true);
      }
    } catch (error) {
      console.error("Favorite error:", error);
      alert(error.message || "Unable to update favorite");
    } finally {
      setFavoriteLoading(false);
    }
  };

  return (
    <article className="group relative flex flex-col justify-between rounded-2xl border border-slate-200/90 bg-white p-5 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md">
      {/* Top row: Station name, ID, Status and Favorite */}
      <div>
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <h3 className="text-base font-bold text-slate-900 group-hover:text-emerald-600 transition-colors truncate">
              {station.name}
            </h3>
            <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
              <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600 font-medium">
                {station.stationId}
              </span>
              {station.spaceId && (
                <span className="text-slate-400">
                  Space <strong className="text-slate-600">{station.spaceId}</strong>
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            <StatusBadge status={station.status} size="sm" />
            <button
              onClick={handleFavorite}
              disabled={favoriteLoading}
              className={`p-1.5 rounded-lg transition-colors focus:outline-none ${
                isFavorite
                  ? "text-amber-500 bg-amber-50 hover:bg-amber-100"
                  : "text-slate-300 hover:text-slate-500 hover:bg-slate-50"
              }`}
              title={isFavorite ? "Remove from favorites" : "Add to favorites"}
              aria-label={isFavorite ? "Remove from favorites" : "Add to favorites"}
            >
              <svg
                className={`w-4 h-4 ${isFavorite ? "fill-current" : "stroke-current fill-none"}`}
                viewBox="0 0 24 24"
                strokeWidth="2"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Prediction visualization bars */}
        <div className="mt-5 space-y-3 pt-3 border-t border-slate-100">
          <PredictionBar
            label="Predicted availability"
            value={availability}
            type="availability"
            size="sm"
          />

          <PredictionBar
            label="Predicted occupancy"
            value={occupancy}
            type="occupancy"
            size="sm"
          />
        </div>
      </div>

      {/* Bottom row: Score & CTA */}
      <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between gap-3">
        {recommendationScore !== null ? (
          <div className="flex flex-col">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
              Smart Score
            </span>
            <div className="flex items-baseline gap-0.5">
              <span className="text-sm font-extrabold font-mono text-teal-700">
                {recommendationScore}
              </span>
              <span className="text-[10px] text-slate-400 font-medium">/100</span>
            </div>
          </div>
        ) : (
          <span className="text-xs text-slate-400">30 min horizon</span>
        )}

        <Link
          to={`/stations/${station.stationId}`}
          className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-3.5 py-1.5 text-xs font-semibold text-white shadow-xs transition-all hover:bg-emerald-600 hover:shadow-emerald-600/20"
        >
          <span>View station</span>
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </article>
  );
}