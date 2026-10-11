import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getStationPrediction } from "../services/stationApi";
import { createSession } from "../services/sessionApi";
import StatusBadge from "../components/StatusBadge";
import PredictionBar from "../components/PredictionBar";
import { DetailsSkeleton } from "../components/LoadingSkeleton";

export default function StationDetails() {
  const { stationId } = useParams();

  const [station, setStation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [startTime, setStartTime] = useState("");
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingMessage, setBookingMessage] = useState("");
  const [bookingSuccess, setBookingSuccess] = useState(false);

  /*
   * Load station prediction using the latest dataset timestamp from backend
   */
  useEffect(() => {
    let cancelled = false;

    const fetchStation = async () => {
      try {
        setLoading(true);
        // Do not pass hardcoded timestamp; let backend resolve the latest valid timestamp
        const result = await getStationPrediction(stationId);

        if (!cancelled) {
          setStation(result);
          setLoading(false);
        }
      } catch (err) {
        console.error("Station details error:", err);
        if (!cancelled) {
          setError(err.message || "Unable to load station details.");
          setLoading(false);
        }
      }
    };

    fetchStation();

    return () => {
      cancelled = true;
    };
  }, [stationId]);

  /*
   * Schedule charging session
   */
  const handleSchedule = async (event) => {
    event.preventDefault();
    setBookingMessage("");
    setBookingSuccess(false);

    if (new Date(startTime) <= new Date()) {
      setBookingMessage("Please select a future charging time.");
      setBookingSuccess(false);
      return;
    }

    try {
      setBookingLoading(true);

      await createSession(
        station.stationId,
        new Date(startTime).toISOString()
      );

      setBookingSuccess(true);
      setBookingMessage("Charging session scheduled successfully.");
      setStartTime("");
    } catch (err) {
      console.error("Schedule session error:", err);
      setBookingSuccess(false);
      setBookingMessage(err.message || "Failed to schedule charging session.");
    } finally {
      setBookingLoading(false);
    }
  };

  /*
   * Minimum date/time for datetime-local
   */
  const minimumDateTime = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");

    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  if (loading) {
    return (
      <main className="flex-1 bg-[#f8fafc] py-8 px-4 sm:px-6 lg:px-8">
        <DetailsSkeleton />
      </main>
    );
  }

  if (error || !station) {
    return (
      <main className="flex-1 bg-[#f8fafc] py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md mx-auto rounded-3xl border border-rose-200 bg-white p-8 text-center shadow-xs space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-slate-900">Station unavailable</h2>
          <p className="text-sm text-slate-500">{error || "Station information could not be found."}</p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-slate-800"
          >
            ← Back to stations
          </Link>
        </div>
      </main>
    );
  }

  const prediction = station.prediction || {};
  const occupancyProbability = (
    Number(prediction.occupancyProbability || 0) * 100
  ).toFixed(1);
  const availabilityProbability = (
    Number(prediction.availabilityProbability || 0) * 100
  ).toFixed(1);
  const isHighOccupancy = Number(prediction.occupancyProbability || 0) >= 0.7;

  return (
    <main className="flex-1 bg-[#f8fafc] py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Back Link */}
        <div>
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>Back to stations</span>
          </Link>
        </div>

        {/* Station Identity & Status Hero Card */}
        <section className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                  {station.stationId}
                </span>
                {station.spaceId && (
                  <span className="text-xs font-medium text-slate-500">
                    Space <strong className="text-slate-800">{station.spaceId}</strong>
                  </span>
                )}
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                {station.name}
              </h1>
            </div>

            <div className="flex items-center gap-3">
              <StatusBadge status={prediction.status || "available"} size="lg" />
            </div>
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6">
            <div className="rounded-2xl bg-slate-50 border border-slate-100 p-4">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Site ID
              </span>
              <span className="text-base font-bold font-mono text-slate-800 mt-1 block">
                {station.siteId || "—"}
              </span>
            </div>

            <div className="rounded-2xl bg-slate-50 border border-slate-100 p-4">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Connector Type
              </span>
              <span className="text-base font-bold text-slate-800 mt-1 block truncate">
                {station.connectorType || "Standard"}
              </span>
            </div>

            <div className="rounded-2xl bg-slate-50 border border-slate-100 p-4">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Connectors
              </span>
              <span className="text-base font-bold font-mono text-slate-800 mt-1 block">
                {station.totalConnectors || 1}
              </span>
            </div>

            <div className="rounded-2xl bg-slate-50 border border-slate-100 p-4">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Prediction Horizon
              </span>
              <span className="text-base font-bold font-mono text-teal-700 mt-1 block">
                {prediction.horizonMinutes || 30} mins
              </span>
            </div>
          </div>
        </section>

        {/* Prediction Insights Section */}
        <section className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs space-y-6">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-teal-50 border border-teal-200/80 text-teal-700 text-xs font-bold uppercase tracking-wider mb-2">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-500"></span>
              ML Forecast
            </div>
            <h2 className="text-xl font-bold text-slate-900">
              30-Minute Occupancy Prediction
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Machine learning forecast trained on historical charging cycles and arrival distributions.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Availability Probability Box */}
            <div className="rounded-2xl bg-emerald-50/60 border border-emerald-200/80 p-5 space-y-3">
              <span className="text-xs font-semibold text-emerald-800 uppercase tracking-wider block">
                Predicted Availability
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl sm:text-4xl font-extrabold font-mono text-emerald-700">
                  {availabilityProbability}%
                </span>
                <span className="text-xs text-emerald-600 font-medium">chance available</span>
              </div>
              <PredictionBar
                value={availabilityProbability}
                type="availability"
                showLabel={false}
                size="md"
              />
            </div>

            {/* Occupancy Probability Box */}
            <div className="rounded-2xl bg-slate-50 border border-slate-200/80 p-5 space-y-3">
              <span className="text-xs font-semibold text-slate-600 uppercase tracking-wider block">
                Predicted Occupancy
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl sm:text-4xl font-extrabold font-mono text-slate-900">
                  {occupancyProbability}%
                </span>
                <span className="text-xs text-slate-500 font-medium">chance occupied</span>
              </div>
              <PredictionBar
                value={occupancyProbability}
                type="occupancy"
                showLabel={false}
                size="md"
              />
            </div>
          </div>

          {/* High Occupancy Warning */}
          {isHighOccupancy ? (
            <div className="rounded-2xl bg-amber-50 border border-amber-200 p-4 flex items-start gap-3 text-amber-800">
              <svg className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div className="text-sm">
                <strong className="font-bold">High occupancy expected</strong>
                <p className="mt-0.5 text-amber-700">
                  This station has a high probability of being occupied during the next 30 minutes. Consider choosing an alternate station with higher availability.
                </p>
              </div>
            </div>
          ) : (
            <div className="rounded-2xl bg-emerald-50/70 border border-emerald-200/70 p-4 flex items-center gap-3 text-emerald-800">
              <svg className="w-5 h-5 text-emerald-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm font-medium text-emerald-900">
                Favorable forecast — Low occupancy expected over the next 30 minutes.
              </p>
            </div>
          )}
        </section>

        {/* Schedule Charging Section */}
        <section className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs space-y-5">
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              Schedule Charging Session
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Reserve a charging slot at this station ahead of time.
            </p>
          </div>

          <form onSubmit={handleSchedule} className="space-y-4 max-w-lg">
            <div>
              <label
                htmlFor="startTime"
                className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2"
              >
                Charging Start Time
              </label>
              <input
                id="startTime"
                type="datetime-local"
                value={startTime}
                min={minimumDateTime()}
                onChange={(e) => setStartTime(e.target.value)}
                required
                className="w-full rounded-xl border border-slate-300 bg-white p-3 text-sm text-slate-900 shadow-xs focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-900/10 font-mono"
              />
            </div>

            <button
              type="submit"
              disabled={bookingLoading}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-6 py-3 text-sm font-bold text-white shadow-md hover:bg-emerald-600 transition-all disabled:opacity-50 disabled:cursor-wait"
            >
              {bookingLoading ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Scheduling...</span>
                </>
              ) : (
                <span>Schedule charging</span>
              )}
            </button>
          </form>

          {/* Booking notification alert */}
          {bookingMessage && (
            <div
              className={`rounded-2xl p-4 text-sm flex items-center gap-3 ${
                bookingSuccess
                  ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                  : "bg-rose-50 text-rose-800 border border-rose-200"
              }`}
            >
              {bookingSuccess ? (
                <svg className="w-5 h-5 text-emerald-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-rose-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
              <span className="font-medium">{bookingMessage}</span>
            </div>
          )}
        </section>

        {/* Quick Links Navigation */}
        <section className="flex items-center gap-3 pt-2">
          <Link
            to="/sessions"
            className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-xs hover:bg-slate-50 transition-colors"
          >
            <span>View My Sessions</span>
            <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
            </svg>
          </Link>
          <Link
            to="/favorites"
            className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-xs hover:bg-slate-50 transition-colors"
          >
            <span>My Favorites</span>
            <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </section>
      </div>
    </main>
  );
}