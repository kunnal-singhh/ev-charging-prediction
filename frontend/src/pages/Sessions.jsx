import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getSessions, updateSession } from "../services/sessionApi";

export default function Sessions() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("all");

  useEffect(() => {
    let cancelled = false;

    const fetchSessions = async () => {
      try {
        setLoading(true);
        const result = await getSessions();

        if (!cancelled) {
          setSessions(result.sessions || []);
          setLoading(false);
        }
      } catch (err) {
        console.error(err);
        if (!cancelled) {
          setError(err.message || "Unable to load sessions");
          setLoading(false);
        }
      }
    };

    fetchSessions();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleCancel = async (sessionId) => {
    try {
      const result = await updateSession(sessionId, {
        status: "cancelled",
      });

      setSessions((currentSessions) =>
        currentSessions.map((session) =>
          session._id === sessionId ? result.session : session
        )
      );
    } catch (err) {
      console.error(err);
      alert(err.message || "Failed to cancel session");
    }
  };

  const categorizedSessions = useMemo(() => {
    const upcoming = sessions.filter(
      (s) => s.status === "scheduled" || s.status === "pending"
    );
    const active = sessions.filter((s) => s.status === "active" || s.status === "in-progress");
    const completed = sessions.filter((s) => s.status === "completed");
    const cancelled = sessions.filter((s) => s.status === "cancelled");

    return { upcoming, active, completed, cancelled };
  }, [sessions]);

  const displayedSessions = useMemo(() => {
    if (activeTab === "upcoming") return categorizedSessions.upcoming;
    if (activeTab === "active") return categorizedSessions.active;
    if (activeTab === "completed") return categorizedSessions.completed;
    if (activeTab === "cancelled") return categorizedSessions.cancelled;
    return sessions;
  }, [activeTab, categorizedSessions, sessions]);

  const getStatusBadge = (status) => {
    const s = String(status || "").toLowerCase();
    if (s === "scheduled") {
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700 border border-blue-200">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
          Scheduled
        </span>
      );
    }
    if (s === "active" || s === "in-progress") {
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 border border-emerald-200">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          Active Charging
        </span>
      );
    }
    if (s === "completed") {
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 border border-slate-200">
          <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
          Completed
        </span>
      );
    }
    if (s === "cancelled") {
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-50 px-2.5 py-1 text-xs font-semibold text-rose-700 border border-rose-200">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
          Cancelled
        </span>
      );
    }
    return (
      <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
        {status}
      </span>
    );
  };

  if (loading) {
    return (
      <main className="flex-1 bg-[#f8fafc] py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="h-8 w-48 rounded skeleton-shimmer" />
          <div className="h-4 w-72 rounded skeleton-shimmer" />
          <div className="space-y-4 pt-4">
            <div className="h-32 rounded-2xl skeleton-shimmer" />
            <div className="h-32 rounded-2xl skeleton-shimmer" />
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex-1 bg-[#f8fafc] py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md mx-auto rounded-3xl border border-rose-200 bg-white p-8 text-center shadow-xs space-y-3">
          <h2 className="text-lg font-bold text-slate-900">Unable to load sessions</h2>
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
              My Charging Sessions
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              View scheduled reservations, ongoing charges, and charging history.
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

        {/* Tab Filters */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 border-b border-slate-200">
          {[
            { id: "all", label: "All Sessions", count: sessions.length },
            { id: "upcoming", label: "Upcoming", count: categorizedSessions.upcoming.length },
            { id: "active", label: "Active", count: categorizedSessions.active.length },
            { id: "completed", label: "Completed", count: categorizedSessions.completed.length },
            { id: "cancelled", label: "Cancelled", count: categorizedSessions.cancelled.length },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`inline-flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-xl transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? "bg-slate-900 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <span>{tab.label}</span>
              <span
                className={`px-1.5 py-0.2 rounded-md font-mono text-[11px] ${
                  activeTab === tab.id ? "bg-slate-800 text-slate-200" : "bg-slate-200/70 text-slate-600"
                }`}
              >
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        {/* Sessions Content */}
        {displayedSessions.length === 0 ? (
          <div className="rounded-3xl border border-slate-200 bg-white p-12 text-center shadow-xs max-w-lg mx-auto space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 className="text-lg font-bold text-slate-900">No charging sessions</h2>
            <p className="text-sm text-slate-500">
              {activeTab === "all"
                ? "You haven't scheduled any charging sessions yet."
                : `No ${activeTab} sessions found.`}
            </p>
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-slate-800 mt-2"
            >
              Browse stations →
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {displayedSessions.map((session) => (
              <div
                key={session._id}
                className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-xs hover:border-slate-300 transition-all space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white font-mono text-sm font-bold">
                      ⚡
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-slate-900">
                        Station {session.stationId}
                      </h3>
                      <span className="text-xs font-mono text-slate-400">
                        ID: {session._id}
                      </span>
                    </div>
                  </div>

                  <div>{getStatusBadge(session.status)}</div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                  <div className="space-y-1">
                    <span className="text-slate-400 font-medium">Start Time</span>
                    <p className="font-semibold text-slate-800 font-mono">
                      {new Date(session.startTime).toLocaleString()}
                    </p>
                  </div>

                  {session.endTime && (
                    <div className="space-y-1">
                      <span className="text-slate-400 font-medium">End Time</span>
                      <p className="font-semibold text-slate-800 font-mono">
                        {new Date(session.endTime).toLocaleString()}
                      </p>
                    </div>
                  )}

                  <div className="space-y-1">
                    <span className="text-slate-400 font-medium">Energy Consumed</span>
                    <p className="font-bold text-slate-900 font-mono text-sm">
                      {session.energyConsumedKwh || 0} kWh
                    </p>
                  </div>
                </div>

                {/* Session Actions */}
                <div className="flex items-center justify-between pt-2">
                  <Link
                    to={`/stations/${session.stationId}`}
                    className="text-xs font-semibold text-slate-600 hover:text-slate-900"
                  >
                    View station details →
                  </Link>

                  {session.status === "scheduled" && (
                    <button
                      onClick={() => handleCancel(session._id)}
                      className="rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-1.5 text-xs font-bold text-rose-700 hover:bg-rose-100 transition-colors focus:outline-none"
                    >
                      Cancel session
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}