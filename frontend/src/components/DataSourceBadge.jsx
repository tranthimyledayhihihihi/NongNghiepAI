const badgeStyles = {
  realtime: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  cached: 'border-blue-200 bg-blue-50 text-blue-700',
  database: 'border-slate-200 bg-slate-50 text-slate-700',
  mock: 'border-amber-200 bg-amber-50 text-amber-700',
  fallback: 'border-amber-200 bg-amber-50 text-amber-700',
  error: 'border-red-200 bg-red-50 text-red-700',
  unknown: 'border-gray-200 bg-gray-50 text-gray-700',
};

const resolveSource = (data = {}) => {
  if (data.is_mock) {
    return { key: 'mock', label: 'Mock' };
  }
  if (data.is_realtime) {
    return { key: 'realtime', label: 'Realtime' };
  }
  if (data.cache_status === 'realtime') {
    return { key: 'realtime', label: 'Realtime' };
  }
  if (data.cache_status === 'hit' || data.cache_status === 'cached') {
    return { key: 'cached', label: 'Cached' };
  }
  if (data.source === 'database' || ['from_db', 'db', 'db_fresh'].includes(data.cache_status)) {
    return { key: 'database', label: 'From DB' };
  }
  if (data.cache_status === 'error') {
    return { key: 'error', label: 'Error' };
  }
  if (data.source === 'fallback') {
    return { key: 'fallback', label: 'Fallback' };
  }
  if (data.source_name) {
    return { key: 'database', label: data.source_name };
  }
  return { key: 'unknown', label: 'Unknown' };
};

const DataSourceBadge = ({ data, className = '' }) => {
  const source = resolveSource(data);
  const titleParts = [
    data?.source_name && `Source: ${data.source_name}`,
    data?.last_updated && `Updated: ${new Date(data.last_updated).toLocaleString('vi-VN')}`,
    data?.observed_at && `Observed: ${new Date(data.observed_at).toLocaleString('vi-VN')}`,
    Number.isFinite(data?.data_age_minutes) && `Age: ${data.data_age_minutes} min`,
    Number.isFinite(data?.cache_age_seconds) && `Age: ${Math.round(data.cache_age_seconds / 60)} min`,
  ].filter(Boolean);

  return (
    <span
      title={titleParts.join(' | ') || source.label}
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badgeStyles[source.key] || badgeStyles.unknown} ${className}`}
    >
      {source.label}
    </span>
  );
};

export default DataSourceBadge;
