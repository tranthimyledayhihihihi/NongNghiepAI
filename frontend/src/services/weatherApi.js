import api from './api';
import { unwrapApiResponse } from '../utils/apiResponse';

export const weatherApi = {
  getCurrentWeather: async (region) => {
    const response = await api.get(`/api/weather/current/${encodeURIComponent(region)}`);
    return unwrapApiResponse(response);
  },

  getForecast: async (region, days = 7) => {
    const response = await api.get(`/api/weather/forecast/${encodeURIComponent(region)}`, {
      params: { days },
    });
    return unwrapApiResponse(response);
  },

  getHourlyForecast: async (region, hours = 24) => {
    const response = await api.get(`/api/weather/hourly/${encodeURIComponent(region)}`, {
      params: { hours },
    });
    return unwrapApiResponse(response);
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
    return unwrapApiResponse(response);
  },

  getRiskAnalysis: async ({ region, cropName }) => {
    const response = await api.get(
      `/api/weather/risk-analysis/${encodeURIComponent(region)}/${encodeURIComponent(cropName || 'lua')}`
    );
    return unwrapApiResponse(response);
  },

  getFarmingRecommendation: async ({ region, cropName }) => {
    const response = await api.get(
      `/api/weather/farming-recommendation/${encodeURIComponent(region)}/${encodeURIComponent(cropName || 'lua')}`
    );
    return unwrapApiResponse(response);
  },

  getAlerts: async ({ region, cropName, growthStage, days = 7 }) => {
    const response = await api.get(`/api/weather/alerts/${encodeURIComponent(region)}`, {
      params: {
        crop_name: cropName || undefined,
        growth_stage: growthStage || undefined,
        days,
      },
    });
    const data = unwrapApiResponse(response);
    return data?.alerts || data;
  },

  getRecommendations: async ({ region, cropName, growthStage }) => {
    const response = await api.get(`/api/weather/recommendations/${encodeURIComponent(region)}`, {
      params: {
        crop_name: cropName || undefined,
        growth_stage: growthStage || undefined,
      },
    });
    const data = unwrapApiResponse(response);
    return data?.recommendations || data;
  },

  refreshCurrentWeather: async (region) => {
    const response = await api.post(`/api/weather/refresh/${encodeURIComponent(region)}`);
    return unwrapApiResponse(response);
  },

  createWeather: async (payload) => {
    const response = await api.post('/api/weather/', payload);
    return unwrapApiResponse(response);
  },
};
