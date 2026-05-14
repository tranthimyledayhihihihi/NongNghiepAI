import api from './api';

export const cropsApi = {
  getCrops: async () => {
    const response = await api.get('/api/crops');
    return response.data;
  },

  searchCrops: async (keyword) => {
    const response = await api.get('/api/crops/search', {
      params: { keyword },
    });
    return response.data;
  },

  getCropDetail: async (cropId) => {
    const response = await api.get(`/api/crops/${cropId}`);
    return response.data;
  },
};
