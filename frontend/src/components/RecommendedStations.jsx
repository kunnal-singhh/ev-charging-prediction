import { Link } from "react-router-dom";
import StatusBadge from "./StatusBadge";

export default function RecommendedStations({ stations }) {
  // The API returns stations in recommendation-rank order.
  const recommendations = (stations || []).slice(0, 4);

  if (recommendations.length === 0) {
    return null;
  }

  return (
    <section className="relative overflow-hidden rounded-3xl border border-slate-200/90 bg-gradient-to-b from-white to-slate-50/50 p-6 sm:p-8 shadow-xs mb-8">
      {/* Background glowing gradient accents */}
      <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/3 -mb-12 w-48 h-48 bg-teal-100/30 rounded-full blur-2xl pointer-events-none" />

      {/* Section Header */}
      <div className="relative z-10 flex flex-col sm:flex-row sm:items-end justify-between gap-2 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200/70 text-emerald-700 text-xs font-bold tracking-wide uppercase mb-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            AI Powered
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Smart recommendations
          </h2>
          <p className="text-sm text-slate-500 mt-1 max-w-xl">
            Stations ranked using current availability and 30-minute occupancy predictions.
          </p>
        </div>
        <span className="text-xs font-medium text-slate-400">
          Top {recommendations.length} options
        </span>
      </div>

      {/* Recommendations Cards Grid */}
      <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {recommendations.map((station, index) => {
          const isTopRank = index === 0;

          const availability = (
            Number(station.availabilityProbability || 0) * 100
          ).toFixed(1);

          const occupancy = (
            Number(station.occupancyProbability || 0) * 100
          ).toFixed(1);

          const score = station.recommendationScore !== undefined && station.recommendationScore !== null
            ? Number(station.recommendationScore).toFixed(1)
            : null;

          return (
            <div
              key={station.stationId}
              className={`relative flex flex-col justify-between rounded-2xl p-5 transition-all duration-200 ${
                isTopRank
                  ? "bg-gradient-to-b from-emerald-50/60 to-white border-2 border-emerald-500/80 shadow-md shadow-emerald-500/5 hover:-translate-y-1 hover:shadow-lg"
                  : "bg-white border border-slate-200 hover:border-slate-300 shadow-xs hover:-translate-y-0.5 hover:shadow-sm"
              }`}
            >
              {isTopRank && (
                <div className="absolute -top-3 left-4 bg-emerald-600 text-white text-[10px] font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded-full shadow-xs">
                  Best Match
                </div>
              )}

              <div>
                {/* Header: Rank + Status */}
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`inline-flex items-center justify-center w-7 h-7 rounded-xl font-mono text-xs font-extrabold ${
                        isTopRank
                          ? "bg-emerald-600 text-white shadow-xs"
                          : "bg-slate-100 text-slate-700"
                      }`}
                    >
                      #{station.recommendationRank || index + 1}
                    </span>
                  </div>
                  <StatusBadge status={station.status} size="sm" />
                </div>

                {/* Station identity */}
                <h3 className="text-base font-bold text-slate-900 truncate mb-1" title={station.name}>
                  {station.name}
                </h3>
                <div className="flex items-center gap-2 text-xs text-slate-500 mb-4">
                  <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">
                    {station.stationId}
                  </span>
                  {station.spaceId && (
                    <span className="text-slate-400">
                      Space <strong className="text-slate-700">{station.spaceId}</strong>
                    </span>
                  )}
                </div>

                {/* Stats row */}
                <div className="grid grid-cols-2 gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-100 mb-4">
                  <div>
                    <span className="block text-[10px] font-medium text-slate-500">
                      Availability
                    </span>
                    <span className="text-sm font-bold font-mono text-emerald-600">
                      {availability}%
                    </span>
                  </div>
                  <div>
                    <span className="block text-[10px] font-medium text-slate-500">
                      Occupancy
                    </span>
                    <span className="text-sm font-bold font-mono text-slate-700">
                      {occupancy}%
                    </span>
                  </div>
                </div>

                {/* Recommendation Score */}
                {score && (
                  <div className="flex items-center justify-between text-xs mb-4 px-1">
                    <span className="text-slate-500 font-medium">Recommendation score</span>
                    <span className="font-mono font-extrabold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-lg border border-teal-100">
                      {score} <span className="text-[10px] text-slate-400">/ 100</span>
                    </span>
                  </div>
                )}
              </div>

              {/* Action Link */}
              <Link
                to={`/stations/${station.stationId}`}
                className={`w-full text-center block rounded-xl py-2 px-3 text-xs font-bold transition-all ${
                  isTopRank
                    ? "bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs"
                    : "bg-slate-900 hover:bg-slate-800 text-white"
                }`}
              >
                View station →
              </Link>
            </div>
          );
        })}
      </div>
    </section>
  );
}
