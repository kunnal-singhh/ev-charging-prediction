/**
 * Skeleton loaders for station cards, recommendations, and dashboards
 */

export function StationCardSkeleton() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-2 flex-1">
          <div className="h-5 w-3/4 rounded-md skeleton-shimmer" />
          <div className="h-3.5 w-1/2 rounded-md skeleton-shimmer" />
        </div>
        <div className="h-6 w-20 rounded-full skeleton-shimmer" />
      </div>

      {/* Space & site */}
      <div className="h-4 w-28 rounded skeleton-shimmer" />

      {/* Predictions */}
      <div className="space-y-3 pt-2">
        <div className="space-y-1.5">
          <div className="flex justify-between">
            <div className="h-3 w-28 rounded skeleton-shimmer" />
            <div className="h-3 w-10 rounded skeleton-shimmer" />
          </div>
          <div className="h-2 w-full rounded-full skeleton-shimmer" />
        </div>

        <div className="space-y-1.5">
          <div className="flex justify-between">
            <div className="h-3 w-28 rounded skeleton-shimmer" />
            <div className="h-3 w-10 rounded skeleton-shimmer" />
          </div>
          <div className="h-2 w-full rounded-full skeleton-shimmer" />
        </div>
      </div>

      {/* Footer */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
        <div className="h-4 w-24 rounded skeleton-shimmer" />
        <div className="h-8 w-28 rounded-xl skeleton-shimmer" />
      </div>
    </div>
  );
}

export function RecommendationSkeleton() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="h-6 w-10 rounded skeleton-shimmer" />
        <div className="h-5 w-20 rounded-full skeleton-shimmer" />
      </div>
      <div className="h-5 w-3/4 rounded skeleton-shimmer" />
      <div className="h-3.5 w-1/2 rounded skeleton-shimmer" />
      <div className="h-8 w-24 rounded skeleton-shimmer" />
      <div className="h-10 w-full rounded-xl skeleton-shimmer" />
    </div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 space-y-2">
      <div className="flex justify-between items-center">
        <div className="h-3 w-24 rounded skeleton-shimmer" />
        <div className="h-7 w-7 rounded-xl skeleton-shimmer" />
      </div>
      <div className="h-8 w-16 rounded skeleton-shimmer" />
    </div>
  );
}

export function DetailsSkeleton() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="h-6 w-36 rounded skeleton-shimmer" />
      <div className="rounded-2xl border border-slate-200 bg-white p-6 space-y-4">
        <div className="flex justify-between items-start">
          <div className="space-y-2">
            <div className="h-7 w-64 rounded skeleton-shimmer" />
            <div className="h-4 w-40 rounded skeleton-shimmer" />
          </div>
          <div className="h-7 w-24 rounded-full skeleton-shimmer" />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-100">
          <div className="h-12 rounded-xl skeleton-shimmer" />
          <div className="h-12 rounded-xl skeleton-shimmer" />
          <div className="h-12 rounded-xl skeleton-shimmer" />
          <div className="h-12 rounded-xl skeleton-shimmer" />
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="h-40 rounded-2xl skeleton-shimmer" />
        <div className="h-40 rounded-2xl skeleton-shimmer" />
      </div>
    </div>
  );
}
