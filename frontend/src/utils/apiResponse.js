export const normalizeApiResponse = (response) => {
  const payload = response?.data ?? response;
  if (!payload || typeof payload !== 'object') return payload;

  if (payload.success && Object.prototype.hasOwnProperty.call(payload, 'data')) {
    const meta = {
      ...(payload.meta || {}),
      source: payload.source ?? payload.meta?.source,
      source_name: payload.source_name ?? payload.meta?.source_name,
      fetched_at: payload.fetched_at ?? payload.meta?.fetched_at,
      updated_at: payload.updated_at ?? payload.meta?.updated_at,
      confidence: payload.confidence ?? payload.meta?.confidence,
      fallback_used: payload.meta?.fallback_used ?? payload.fallback_used,
      timeout: payload.meta?.timeout ?? payload.timeout,
      error: payload.meta?.error ?? payload.error,
      cache_status: payload.meta?.cache_status ?? payload.cache_status,
      message: payload.message,
    };

    if (Array.isArray(payload.data)) {
      return Object.assign([...payload.data], {
        meta,
        source: meta.source,
        source_name: meta.source_name,
        fallback_used: meta.fallback_used,
        timeout: meta.timeout,
      });
    }

    if (payload.data && typeof payload.data === 'object') {
      return {
        ...payload.data,
        source: payload.data.source ?? meta.source,
        source_name: payload.data.source_name ?? meta.source_name,
        fetched_at: payload.data.fetched_at ?? meta.fetched_at,
        updated_at: payload.data.updated_at ?? meta.updated_at,
        confidence: payload.data.confidence ?? meta.confidence,
        fallback_used: payload.data.fallback_used ?? meta.fallback_used,
        timeout: payload.data.timeout ?? meta.timeout,
        error: payload.data.error ?? meta.error,
        cache_status: payload.data.cache_status ?? meta.cache_status,
        message: payload.data.message ?? meta.message,
        meta: {
          ...meta,
          ...(payload.data.meta || {}),
        },
      };
    }

    return {
      data: payload.data,
      ...meta,
      meta,
    };
  }

  return payload;
};
