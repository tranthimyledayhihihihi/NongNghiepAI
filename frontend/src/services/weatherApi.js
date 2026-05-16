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

  getHourlyForecast: async (region, hours = 24) => {
    const response = await api.get(`/api/weather/hourly/${encodeURIComponent(region)}`, {
      params: { hours },
    });
    return response.data;
  },

  getAgricultureWeather: async ({ region, cropName, growthStage, days = 7, includeHourly = true }) => {
    const response = await api.get(`/api/weather/agriculture/${encodeURIComponent(region)}`, {
      params: {
        crop_name: cropName || undefined,
        growth_stage: growthStage || undefined,
        days,
        include_hourly: includeHourly,
      },
    });
    return response.data;
  },

  getAlerts: async ({ region, cropName, growthStage, days = 7 }) => {
    const response = await api.get(`/api/weather/alerts/${encodeURIComponent(region)}`, {
      params: {
        crop_name: cropName || undefined,
        growth_stage: growthStage || undefined,
        days,
      },
    });
    return response.data;
  },

  getRecommendations: async ({ region, cropName, growthStage }) => {
    const response = await api.get(`/api/weather/recommendations/${encodeURIComponent(region)}`, {
      params: {
        crop_name: cropName || undefined,
        growth_stage: growthStage || undefined,
      },
    });
    return response.data;
  },

  refreshCurrentWeather: async (region) => {
    const response = await api.post(`/api/weather/refresh/${encodeURIComponent(region)}`);
    return response.data;
  },

  createWeather: async (payload) => {
    const response = await api.post('/api/weather/', payload);
    return response.data;
  },
};
