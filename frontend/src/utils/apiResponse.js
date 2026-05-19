export function dedupeMessages(messages = []) {
  return [
    ...new Set(
      messages
        .filter(Boolean)
        .map((message) => String(message).trim())
        .filter(Boolean)
    ),
  ];
}

export function normalizeApiResponse(response) {
  const payload = response?.data ?? response;
  if (!payload || typeof payload !== 'object') {
    return {
      success: false,
      data: null,
      source: 'unknown',
      isRealtime: false,
      isCache: false,
      isMock: false,
      warning: null,
      error: {
        code: 'INVALID_RESPONSE',
        message: 'Không thể tải dữ liệu realtime.',
      },
    };
  }

  const metadata = {
    ...(payload.metadata || {}),
    ...(payload.meta || {}),
  };
  const hasEnvelope = Object.prototype.hasOwnProperty.call(payload, 'success')
    || Object.prototype.hasOwnProperty.call(payload, 'data')
    || Object.prototype.hasOwnProperty.call(payload, 'meta')
    || Object.prototype.hasOwnProperty.call(payload, 'metadata')
    || Object.prototype.hasOwnProperty.call(payload, 'error');
  const data = Object.prototype.hasOwnProperty.call(payload, 'data')
    ? payload.data ?? null
    : (hasEnvelope ? null : payload);
  const warnings = [
    ...(Array.isArray(payload.warning) ? payload.warning : [payload.warning]),
    ...(Array.isArray(metadata.warning) ? metadata.warning : [metadata.warning]),
  ];
  const source = payload.source ?? metadata.source ?? metadata.source_type ?? data?.source ?? 'unknown';
  const rawSource = String(source).toLowerCase();
  const cacheStatus = String(payload.cache_status ?? metadata.cache_status ?? data?.cache_status ?? '').toLowerCase();
  const sourceName = payload.source_name ?? metadata.source_name ?? data?.source_name ?? source;
  const isRealtime = payload.is_realtime === true || metadata.is_realtime === true || data?.is_realtime === true;
  const isCache = payload.is_cache === true
    || metadata.is_cache === true
    || data?.is_cache === true
    || ['cache', 'cached', 'fallback'].includes(rawSource)
    || ['cached', 'hit', 'from_cache', 'stale'].includes(cacheStatus);
  const isMock = payload.is_mock === true || metadata.is_mock === true || data?.is_mock === true || rawSource === 'mock';

  const normalized = {
    success: payload.success === true || (payload.success === undefined && data !== null),
    data,
    source,
    sourceName,
    source_name: sourceName,
    isRealtime,
    is_realtime: isRealtime,
    isCache,
    is_cache: isCache,
    isMock,
    is_mock: isMock,
    warning: dedupeMessages(warnings).join(' | ') || null,
    error: payload.error ?? metadata.error ?? null,
    message: payload.message,
    fetched_at: payload.fetched_at ?? metadata.fetched_at ?? data?.fetched_at,
    updated_at: payload.updated_at ?? metadata.updated_at ?? data?.updated_at,
    confidence: payload.confidence ?? metadata.confidence ?? data?.confidence,
    cache_status: cacheStatus,
    meta: metadata,
  };

  if (data && typeof data === 'object' && !Array.isArray(data)) {
    return {
      ...data,
      ...normalized,
      data,
      meta: {
        ...metadata,
        ...(data.meta || {}),
      },
    };
  }

  if (Array.isArray(data)) {
    return Object.assign([...data], normalized, {
      data,
      meta: metadata,
    });
  }

  return normalized;
}

export function normalizeApiError(error) {
  if (error?.success === false && error?.error) return error;

  const payload = error?.response?.data;
  const message =
    payload?.error?.message ||
    payload?.message ||
    error?.friendlyMessage ||
    error?.message ||
    'Không thể tải dữ liệu realtime.';

  return {
    success: false,
    data: null,
    source: payload?.source || 'realtime_api',
    sourceName: payload?.source_name || payload?.source || 'realtime_api',
    source_name: payload?.source_name || payload?.source || 'realtime_api',
    isRealtime: false,
    is_realtime: false,
    isCache: false,
    is_cache: false,
    isMock: false,
    is_mock: false,
    warning: null,
    error: {
      code: payload?.error?.code || error?.code || 'API_ERROR',
      message,
    },
    message,
  };
}

export function ensureApiSuccess(response) {
  const normalized = normalizeApiResponse(response);
  if (normalized.success === false) {
    throw normalized;
  }
  return normalized;
}
