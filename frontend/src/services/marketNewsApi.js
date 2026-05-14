import api from './api';

export const marketNewsApi = {
  getLatest: async (limit = 6) => {
    const response = await api.get('/api/market-news/', { params: { limit } });
    return response.data;
  },
  refresh: async () => {
    const response = await api.post('/api/market-news/refresh');
    return response.data;
  },
};
