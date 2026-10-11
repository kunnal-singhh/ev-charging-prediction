/**
 * StatusBadge - Premium visual status indicator for EV Charging Stations
 * Shows both color dot indicator and semantic status text for accessibility.
 */
export default function StatusBadge({ status, size = 'md' }) {
  const isAvailable = status === 'available';
  const isOccupied = status === 'occupied';

  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5 gap-1.5 font-semibold',
    md: 'text-xs px-2.5 py-1 gap-2 font-semibold',
    lg: 'text-sm px-3.5 py-1.5 gap-2.5 font-bold',
  };

  const dotSizes = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-2.5 h-2.5',
  };

  if (isAvailable) {
    return (
      <span
        className={`inline-flex items-center rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/80 shadow-xs tracking-wide uppercase ${sizeClasses[size] || sizeClasses.md}`}
        role="status"
        aria-label="Status: Available"
      >
        <span className={`${dotSizes[size] || dotSizes.md} rounded-full bg-emerald-500 animate-pulse-subtle`}></span>
        Available
      </span>
    );
  }

  if (isOccupied) {
    return (
      <span
        className={`inline-flex items-center rounded-full bg-rose-50 text-rose-700 border border-rose-200/80 shadow-xs tracking-wide uppercase ${sizeClasses[size] || sizeClasses.md}`}
        role="status"
        aria-label="Status: Occupied"
      >
        <span className={`${dotSizes[size] || dotSizes.md} rounded-full bg-rose-500`}></span>
        Occupied
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center rounded-full bg-slate-100 text-slate-600 border border-slate-200 tracking-wide uppercase ${sizeClasses[size] || sizeClasses.md}`}
      role="status"
      aria-label={`Status: ${status || 'Unknown'}`}
    >
      <span className={`${dotSizes[size] || dotSizes.md} rounded-full bg-slate-400`}></span>
      {status || 'Unknown'}
    </span>
  );
}
