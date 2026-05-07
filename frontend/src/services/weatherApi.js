import api from './api';

export const weatherApi = {
  getCurrentWeather: async (region) => {
    const response = await api.get(`/api/weather/current/${encodeURIComponent(region)}`);
    return response.data;
  },

  getForecast: async (region, days = 7) => {
    const response = await api.get(`/api/weather/forecast/${encodeURIComponent(region)}`, {
      params: { days },
    });
    return response.data;
  },

  createWeather: async (payload) => {
    const response = await api.post('/api/weather/', payload);
    return response.data;
  },
};
