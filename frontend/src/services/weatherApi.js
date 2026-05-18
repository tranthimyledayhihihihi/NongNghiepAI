import api from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

export const weatherApi = {
  getCurrentWeather: async (region) => {
    const response = await api.get(`/api/weather/current/${encodeURIComponent(region)}`);
    return normalizeApiResponse(response);
  },

  getForecast: async (region, days = 7) => {
    const response = await api.get(`/api/weather/forecast/${encodeURIComponent(region)}`, {
      params: { days },
    });
    return normalizeApiResponse(response);
  },

  getHourlyForecast: async (region, hours = 24) => {
    const response = await api.get(`/api/weather/hourly/${encodeURIComponent(region)}`, {
      params: { hours },
    });
    return normalizeApiResponse(response);
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
    return normalizeApiResponse(response);
  },

  getRiskAnalysis: async ({ region, cropName }) => {
    const response = await api.get(
      `/api/weather/risk-analysis/${encodeURIComponent(region)}/${encodeURIComponent(cropName || 'lua')}`
    );
    return normalizeApiResponse(response);
  },

  getFarmingRecommendation: async ({ region, cropName }) => {
    const response = await api.get(
      `/api/weather/farming-recommendation/${encodeURIComponent(region)}/${encodeURIComponent(cropName || 'lua')}`
    );
    return normalizeApiResponse(response);
  },

  getAlerts: async ({ region, cropName, growthStage, days = 7 }) => {
    const response = await api.get(`/api/weather/alerts/${encodeURIComponent(region)}`, {
      params: {
        crop_name: cropName || undefined,
        growth_stage: growthStage || undefined,
        days,
      },
    });
    const data = normalizeApiResponse(response);
    return data.alerts || data;
  },

  getRecommendations: async ({ region, cropName, growthStage }) => {
    const response = await api.get(`/api/weather/recommendations/${encodeURIComponent(region)}`, {
      params: {
        crop_name: cropName || undefined,
        growth_stage: growthStage || undefined,
      },
    });
    const data = normalizeApiResponse(response);
    return data.recommendations || data;
  },

  refreshCurrentWeather: async (region) => {
    const response = await api.post(`/api/weather/refresh/${encodeURIComponent(region)}`);
    return normalizeApiResponse(response);
  },

  createWeather: async (payload) => {
    const response = await api.post('/api/weather/', payload);
    return normalizeApiResponse(response);
  },
};
