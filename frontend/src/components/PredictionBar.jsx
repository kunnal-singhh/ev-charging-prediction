/**
 * PredictionBar - Visual indicator for availability & occupancy percentages
 */
export default function PredictionBar({
  label,
  value,
  type = 'availability',
  showLabel = true,
  size = 'md',
}) {
  const numericValue = Math.min(100, Math.max(0, Number(value) || 0));
  const formattedValue = numericValue.toFixed(1);

  // Determine bar colors based on metric type and value threshold
  let barGradient = 'bg-emerald-500';
  let trackColor = 'bg-slate-100';
  let textColor = 'text-slate-900';

  if (type === 'availability') {
    if (numericValue >= 70) {
      barGradient = 'bg-emerald-500';
    } else if (numericValue >= 40) {
      barGradient = 'bg-amber-500';
    } else {
      barGradient = 'bg-rose-500';
    }
  } else if (type === 'occupancy') {
    if (numericValue >= 70) {
      barGradient = 'bg-rose-500';
      textColor = 'text-rose-600';
    } else if (numericValue >= 40) {
      barGradient = 'bg-amber-500';
    } else {
      barGradient = 'bg-emerald-500';
    }
  }

  const heightClasses = {
    sm: 'h-1.5',
    md: 'h-2',
    lg: 'h-2.5',
  };

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-slate-500 font-medium">{label}</span>
          <span className={`font-mono font-semibold ${textColor}`}>
            {formattedValue}%
          </span>
        </div>
      )}
      <div className={`w-full ${trackColor} rounded-full overflow-hidden ${heightClasses[size] || heightClasses.md}`}>
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${barGradient}`}
          style={{ width: `${numericValue}%` }}
          role="progressbar"
          aria-valuenow={numericValue}
          aria-valuemin="0"
          aria-valuemax="100"
          aria-label={label || 'Prediction bar'}
        />
      </div>
    </div>
  );
}
