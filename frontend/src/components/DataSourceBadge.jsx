const badgeStyles = {
  realtime: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  ai: 'border-violet-200 bg-violet-50 text-violet-700',
  cached: 'border-blue-200 bg-blue-50 text-blue-700',
  database: 'border-slate-200 bg-slate-50 text-slate-700',
  mock: 'border-amber-200 bg-amber-50 text-amber-700',
  fallback: 'border-amber-200 bg-amber-50 text-amber-700',
  error: 'border-red-200 bg-red-50 text-red-700',
  unknown: 'border-gray-200 bg-gray-50 text-gray-700',
};

const resolveSource = (data = {}) => {
  const meta = data.meta || {};
  const source = data.source || meta.source || '';
  const cacheStatus = data.cache_status || meta.cache_status || '';
  const isMock = data.is_mock || meta.is_mock;
  const isRealtime = data.is_realtime || meta.is_realtime;

  if (isMock || source === 'mock' || cacheStatus === 'mock') return { key: 'mock', label: 'Mock/Demo' };
  if (isRealtime || source === 'realtime_api' || cacheStatus === 'live' || cacheStatus === 'realtime') {
    return { key: 'realtime', label: 'Realtime API' };
  }
  if (source === 'ai_generated') return { key: 'ai', label: 'AI Generated' };
  if (source === 'cached' || ['cached', 'hit', 'from_cache', 'stale'].includes(cacheStatus)) {
    return { key: 'cached', label: 'Cached' };
  }
  if (source === 'database' || ['from_db', 'db', 'db_fresh'].includes(cacheStatus)) {
    return { key: 'database', label: 'Database' };
  }
  if (cacheStatus === 'error') return { key: 'error', label: 'Error' };
  if (source === 'fallback') return { key: 'fallback', label: 'Fallback' };
  if (data.source_name || meta.source_name) return { key: 'database', label: data.source_name || meta.source_name };
  return { key: 'unknown', label: 'Unknown' };
};

const formatDateTime = (value) => {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString('vi-VN');
};

const DataSourceBadge = ({ data = {}, className = '' }) => {
  const source = resolveSource(data);
  const meta = data.meta || {};
  const fetchedAt = data.fetched_at || meta.fetched_at;
  const lastUpdated = data.last_updated || meta.last_updated || data.updated_at || data.created_at;
  const confidence = data.confidence ?? meta.confidence;
  const sourceName = data.source_name || meta.source_name;
  const titleParts = [
    sourceName && `Source: ${sourceName}`,
    fetchedAt && `Fetched: ${formatDateTime(fetchedAt)}`,
    lastUpdated && `Updated: ${formatDateTime(lastUpdated)}`,
    Number.isFinite(Number(confidence)) && `Confidence: ${(Number(confidence) * 100).toFixed(0)}%`,
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
