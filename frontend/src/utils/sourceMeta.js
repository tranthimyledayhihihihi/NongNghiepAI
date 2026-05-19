const SOURCE_LABELS = {
  realtime_api: 'Dữ liệu thời gian thực',
  database: 'Dữ liệu hệ thống',
  cached: 'Dữ liệu cache',
  ai_generated: 'Dữ liệu do AI tạo',
  mock: 'Dữ liệu mô phỏng',
  legacy: 'Dữ liệu cũ',
};

const SOURCE_KEYS = {
  realtime_api: 'realtime',
  database: 'database',
  cached: 'cached',
  ai_generated: 'ai',
  mock: 'mock',
  legacy: 'legacy',
};

export const normalizeSourceMeta = (item = {}, defaultSource = 'database') => {
  const meta = item?.meta || {};
  const source = String(item?.source || meta.source || defaultSource).toLowerCase();
  const cacheStatus = String(item?.cache_status || meta.cache_status || '').toLowerCase();
  const fallbackUsed = Boolean(item?.fallback_used || meta.fallback_used);
  const timeout = Boolean(item?.timeout || meta.timeout);
  const isMock = Boolean(item?.is_mock || meta.is_mock);
  const isCache = Boolean(item?.is_cache || meta.is_cache);
  const isRealtime = Boolean(item?.is_realtime || meta.is_realtime);

  let normalized = source;
  if (isMock || source === 'mock' || cacheStatus === 'mock') normalized = 'mock';
  else if (
    isCache ||
    fallbackUsed ||
    timeout ||
    ['cache', 'cached', 'fallback'].includes(source) ||
    ['hit', 'from_cache', 'stale', 'cached'].includes(cacheStatus)
  ) normalized = 'cached';
  else if (isRealtime || cacheStatus === 'live' || ['realtime', 'realtime_api', 'open-meteo', 'rss'].includes(source)) normalized = 'realtime_api';
  else if (['from_db', 'db', 'db_fresh'].includes(cacheStatus)) normalized = 'database';
  else if (['db', 'market_db'].includes(source)) normalized = 'database';
  else if (['ai', 'rule_based_ai', 'explainable_rule_ai'].includes(source)) normalized = 'ai_generated';
  else if (source === 'legacy') normalized = 'legacy';
  else if (!SOURCE_LABELS[normalized]) normalized = defaultSource;

  return {
    source: normalized,
    source_name: item?.source_name || meta.source_name || SOURCE_LABELS[normalized] || normalized,
    fetched_at: item?.fetched_at || meta.fetched_at,
    updated_at: item?.updated_at || item?.last_updated || item?.created_at || meta.updated_at || meta.last_updated,
    confidence: item?.confidence ?? meta.confidence,
    cache_status: cacheStatus,
    fallback_used: fallbackUsed,
    timeout,
    error: item?.error || meta.error,
    is_mock: isMock || normalized === 'mock',
    is_cache: isCache || normalized === 'cached',
    is_realtime: isRealtime || normalized === 'realtime_api',
  };
};

export const formatUpdatedTime = (value) => {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString('vi-VN');
};

export const getSourceBadgeProps = (item = {}, defaultSource = 'database') => {
  const meta = normalizeSourceMeta(item, defaultSource);
  return {
    key: SOURCE_KEYS[meta.source] || 'unknown',
    label: SOURCE_LABELS[meta.source] || meta.source_name || 'Không rõ',
    meta,
  };
};
