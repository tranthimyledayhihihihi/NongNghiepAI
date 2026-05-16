import api from './api';

const unwrap = (response) => response.data?.data ?? response.data;

export const dashboardApi = {
  getSummary: async (region, { cropName = 'lua', forceRefresh = false } = {}) => {
    const response = await api.get('/api/dashboard/summary', {
      params: {
        region: region || undefined,
        crop_name: cropName,
        force_refresh: forceRefresh,
      },
    });
    return unwrap(response);
  },

  getFeaturedCrop: async (region, { cropName = 'lua', forceRefresh = false } = {}) => {
    const response = await api.get('/api/dashboard/featured-crop', {
      params: {
        region: region || undefined,
        crop_name: cropName,
        force_refresh: forceRefresh,
      },
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

  getWeatherRisk: async ({ region, cropName = 'lua', growthStage, forceRefresh = false } = {}) => {
    const response = await api.get('/api/dashboard/weather-risk', {
      params: {
        region: region || undefined,
        crop_name: cropName,
        growth_stage: growthStage || undefined,
        force_refresh: forceRefresh,
      },
    });
    return unwrap(response);
  },

  getRegionalPrices: async ({ cropName = 'lua', regions, forceRefresh = false } = {}) => {
    const response = await api.get('/api/dashboard/regional-prices', {
      params: {
        crop_name: cropName,
        regions,
        force_refresh: forceRefresh,
      },
      paramsSerializer: {
        indexes: null,
      },
    });
    return unwrap(response);
  },

  getRealtimeMarket: async ({ cropName = 'lua', region, forceRefresh = false } = {}) => {
    const response = await api.get('/api/dashboard/realtime-market', {
      params: {
        crop_name: cropName,
        region: region || undefined,
        force_refresh: forceRefresh,
      },
    });
    return unwrap(response);
  },

  getNews: async ({ limit = 6, cropName, region, forceRefresh = false } = {}) => {
    const response = await api.get('/api/dashboard/news', {
      params: {
        limit,
        crop_name: cropName || undefined,
        region: region || undefined,
        force_refresh: forceRefresh,
      },
    });
    return unwrap(response);
  },

  getDataHealth: async ({ cropName = 'lua', region } = {}) => {
    const response = await api.get('/api/dashboard/data-health', {
      params: {
        crop_name: cropName,
        region: region || undefined,
      },
    });
    return unwrap(response);
  },

  refresh: async ({ source = 'all', cropName = 'lua', region } = {}) => {
    const response = await api.post('/api/dashboard/refresh', null, {
      params: {
        source,
        crop_name: cropName,
        region: region || undefined,
      },
    });
    return unwrap(response);
  },

  reset: async ({ cropName = 'lua', region } = {}) => {
    const response = await api.post('/api/dashboard/reset', null, {
      params: {
        crop_name: cropName,
        region: region || undefined,
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
