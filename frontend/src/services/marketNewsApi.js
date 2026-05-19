import api, { getApiErrorMessage } from './api';
import { normalizeApiError, normalizeApiResponse } from '../utils/apiResponse';

const request = async (factory, fallback) => {
  try {
    return normalizeApiResponse(await factory());
  } catch (error) {
    throw normalizeApiError({ ...error, message: getApiErrorMessage(error, fallback) });
  }
};

const normalizeNewsPayload = (payload) => (
  Array.isArray(payload)
    ? { news: payload, metadata: payload.meta || {}, source: payload.source, source_name: payload.source_name }
    : payload
);

export const marketNewsApi = {
  getLatest: async (limit = 6, { crop, cropName, region } = {}) => {
    const payload = await request(() => api.get('/api/market/news', {
      params: {
        limit,
        crop: crop || cropName || undefined,
        region: region || undefined,
      },
    }), 'Không thể tải tin tức thị trường realtime.');
    return normalizeNewsPayload(payload);
  },
  refresh: async () => {
    return request(() => api.post('/api/market-news/refresh'), 'Không làm mới được tin tức thị trường');
  },
};

marketNewsApi.getLegacyLatest = async (limit = 6) => {
  return request(() => api.get('/api/market-news/', { params: { limit } }), 'Không thể tải tin tức thị trường realtime.');
};
