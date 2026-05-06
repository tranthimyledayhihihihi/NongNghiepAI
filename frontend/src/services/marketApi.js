import api from './api';

export const marketApi = {
  getChannels: async () => {
    const response = await api.get('/api/market/channels');
    return response.data;
  },

  suggestMarket: async (cropName, region, quantity, qualityGrade = 'grade_1') => {
    const response = await api.post('/api/market/suggest', {
      crop_name: cropName,
      region,
      quantity: Number(quantity),
      quality_grade: qualityGrade,
    });
    return response.data;
  },

  getHistory: async (userId = 1, limit = 50) => {
    const response = await api.get(`/api/market/history/${encodeURIComponent(userId)}`, {
      params: { limit },
    });
    return response.data;
  },

  getDemand: async (cropName) => {
    const response = await api.get(`/api/market/demand/${encodeURIComponent(cropName)}`);
    return response.data;
  },
};
