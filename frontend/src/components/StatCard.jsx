/**
 * StatCard - Compact, high-density metric card for EVConnect dashboard
 */
export default function StatCard({
  title,
  value,
  subtitle,
  icon,
  variant = 'default',
}) {
  const variantStyles = {
    default: {
      card: 'bg-white border-slate-200/80',
      badge: 'bg-slate-100 text-slate-700',
      valueText: 'text-slate-900',
    },
    success: {
      card: 'bg-white border-emerald-200/70 hover:border-emerald-300',
      badge: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
      valueText: 'text-emerald-600',
    },
    danger: {
      card: 'bg-white border-rose-200/70 hover:border-rose-300',
      badge: 'bg-rose-50 text-rose-700 border border-rose-100',
      valueText: 'text-rose-600',
    },
    accent: {
      card: 'bg-white border-teal-200/70 hover:border-teal-300',
      badge: 'bg-teal-50 text-teal-700 border border-teal-100',
      valueText: 'text-teal-700',
    },
  };

  const currentVariant = variantStyles[variant] || variantStyles.default;

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border p-4 sm:p-5 transition-all duration-200 hover:shadow-sm ${currentVariant.card}`}
    >
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </span>
        {icon && (
          <div className={`flex h-8 w-8 items-center justify-center rounded-xl text-sm ${currentVariant.badge}`}>
            {icon}
          </div>
        )}
      </div>

      <div className="mt-2 flex items-baseline gap-2">
        <span className={`text-2xl sm:text-3xl font-extrabold font-mono tracking-tight ${currentVariant.valueText}`}>
          {value}
        </span>
        {subtitle && (
          <span className="text-xs font-medium text-slate-400">
            {subtitle}
          </span>
        )}
      </div>
    </div>
  );
}
