import api from './api';

const unwrap = (response) => response.data?.data ?? response.data;

export const dashboardApi = {
  getSummary: async (region, { forceRefresh = false } = {}) => {
    const response = await api.get('/api/dashboard/summary', {
      params: {
        region: region || undefined,
        force_refresh: forceRefresh,
      },
    });
    return unwrap(response);
  },

  getFeaturedCrop: async (region) => {
    const response = await api.get('/api/dashboard/featured-crop', {
      params: region ? { region } : undefined,
    });
    return unwrap(response);
  },

  getPriceTrend: async ({ cropName = 'lua', region, days = 7 } = {}) => {
    const response = await api.get('/api/dashboard/price-trend', {
      params: {
        crop_name: cropName,
        region: region || undefined,
        days,
      },
    });
    return unwrap(response);
  },

  getWeatherOverview: async (region, { forceRefresh = false } = {}) => {
    const response = await api.get('/api/dashboard/weather-overview', {
      params: {
        region: region || undefined,
        force_refresh: forceRefresh,
      },
    });
    return unwrap(response);
  },

  getAiRecommendation: async ({ cropName = 'lua', region } = {}) => {
    const response = await api.get('/api/dashboard/ai-recommendation', {
      params: {
        crop_name: cropName,
        region: region || undefined,
      },
    });
    return unwrap(response);
  },
};
