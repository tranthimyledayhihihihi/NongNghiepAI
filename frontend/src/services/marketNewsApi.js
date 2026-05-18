import api, { getApiErrorMessage } from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

const request = async (factory, fallback) => {
  try {
    return normalizeApiResponse(await factory());
  } catch (error) {
    error.message = getApiErrorMessage(error, fallback);
    throw error;
  }
};

export const marketNewsApi = {
  getLatest: async (limit = 6, { crop, region } = {}) => {
    return request(() => api.get('/api/market/news', {
      params: {
        limit,
        crop: crop || undefined,
        region: region || undefined,
      },
    }), 'Khong tai duoc market news');
  },
  refresh: async () => {
    return request(() => api.post('/api/market-news/refresh'), 'Khong refresh duoc legacy market news');
  },
};

marketNewsApi.getLegacyLatest = async (limit = 6) => {
  return request(() => api.get('/api/market-news/', { params: { limit } }), 'Khong tai duoc legacy market news');
};
