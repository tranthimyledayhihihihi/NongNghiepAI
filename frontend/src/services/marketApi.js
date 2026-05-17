import api from './api';

const unwrap = (response) => response.data?.data ?? response.data;

export const marketApi = {
  getChannels: async () => {
    const response = await api.get('/api/market/channels');
    return unwrap(response);
  },

  getNews: async ({ limit = 10, crop, region } = {}) => {
    const response = await api.get('/api/market/news', {
      params: {
        limit,
        crop: crop || undefined,
        region: region || undefined,
      },
    });
    return unwrap(response);
  },

  getPrices: async ({ crop = 'lua', region = 'Ha Noi' } = {}) => {
    const response = await api.get('/api/market/prices', {
      params: { crop, region },
    });
    return unwrap(response);
  },

  analyzeNews: async ({ title, summary, crop, region }) => {
    const response = await api.post('/api/market/analyze-news', {
      title,
      summary,
      crop,
      region,
    });
    return unwrap(response);
  },

  getTrends: async ({ crop = 'lua', region = 'Ha Noi' } = {}) => {
    const response = await api.get('/api/market/trends', {
      params: { crop, region },
    });
    return unwrap(response);
  },

  getOpportunities: async ({ crop = 'lua', region = 'Ha Noi' } = {}) => {
    const response = await api.get('/api/market/opportunities', {
      params: { crop, region },
    });
    return unwrap(response);
  },

  getRisks: async ({ crop = 'lua', region = 'Ha Noi' } = {}) => {
    const response = await api.get('/api/market/risks', {
      params: { crop, region },
    });
    return unwrap(response);
  },

  suggestMarket: async (cropName, region, quantity, qualityGrade = 'grade_1') => {
    const response = await api.post('/api/market/suggest', {
      crop_name: cropName,
      region,
      quantity: Number(quantity),
      quality_grade: qualityGrade,
    });
    return unwrap(response);
  },

  getHistory: async (userId = 1, limit = 50) => {
    const response = await api.get(`/api/market/history/${encodeURIComponent(userId)}`, {
      params: { limit },
    });
    return unwrap(response);
  },

  getDemand: async (cropName) => {
    const response = await api.get(`/api/market/demand/${encodeURIComponent(cropName)}`);
    return unwrap(response);
  },
};
