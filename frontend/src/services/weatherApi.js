import api from './api';

export const weatherApi = {
  getCurrentWeather: async (region) => {
    const response = await api.get(`/api/weather/current/${encodeURIComponent(region)}`);
    return response.data;
  },

  createWeather: async (payload) => {
    const response = await api.post('/api/weather/', payload);
    return response.data;
  },
};
