import { formatUpdatedTime, getSourceBadgeProps } from '../utils/sourceMeta';

const badgeStyles = {
  realtime: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  ai: 'border-violet-200 bg-violet-50 text-violet-700',
  cached: 'border-blue-200 bg-blue-50 text-blue-700',
  database: 'border-slate-200 bg-slate-50 text-slate-700',
  mock: 'border-amber-200 bg-amber-50 text-amber-700',
  legacy: 'border-orange-200 bg-orange-50 text-orange-700',
  error: 'border-red-200 bg-red-50 text-red-700',
  unknown: 'border-gray-200 bg-gray-50 text-gray-700',
};

const DataSourceBadge = ({
  data = {},
  source,
  sourceName,
  fetchedAt,
  updatedAt,
  confidence,
  compact = false,
  className = '',
}) => {
  const merged = {
    ...(data || {}),
    source: source || data?.source,
    source_name: sourceName || data?.source_name,
    fetched_at: fetchedAt || data?.fetched_at,
    updated_at: updatedAt || data?.updated_at,
    confidence: confidence ?? data?.confidence,
  };
  const sourceInfo = getSourceBadgeProps(merged);
  const { meta } = sourceInfo;
  const titleParts = [
    meta.source_name && `Source: ${meta.source_name}`,
    meta.fetched_at && `Fetched: ${formatUpdatedTime(meta.fetched_at)}`,
    meta.updated_at && `Updated: ${formatUpdatedTime(meta.updated_at)}`,
    Number.isFinite(Number(meta.confidence)) && `Confidence: ${(Number(meta.confidence) * 100).toFixed(0)}%`,
    meta.fallback_used && 'Fallback: yes',
    meta.timeout && 'Timeout: yes',
    meta.error && `Error: ${meta.error}`,
    Number.isFinite(merged?.data_age_minutes) && `Age: ${merged.data_age_minutes} min`,
    Number.isFinite(merged?.cache_age_seconds) && `Age: ${Math.round(merged.cache_age_seconds / 60)} min`,
  ].filter(Boolean);
  const displayName = meta.source_name && meta.source_name !== sourceInfo.label ? meta.source_name : null;
  const displayTime = formatUpdatedTime(meta.updated_at || meta.fetched_at);

  return (
    <span
      title={titleParts.join(' | ') || sourceInfo.label}
      className={`inline-flex max-w-full items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-semibold ${badgeStyles[sourceInfo.key] || badgeStyles.unknown} ${className}`}
    >
      <span>{sourceInfo.label}</span>
      {!compact && displayName && (
        <span className="hidden max-w-[9rem] truncate opacity-80 sm:inline">| {displayName}</span>
      )}
      {!compact && displayTime && (
        <span className="hidden max-w-[7rem] truncate opacity-70 md:inline">| {displayTime}</span>
      )}
    </span>
  );
};

export default DataSourceBadge;
