import api, { getApiErrorMessage, settledValue } from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

const unwrap = (response) => normalizeApiResponse(response);
const request = async (factory, fallback) => {
  try {
    return unwrap(await factory());
  } catch (error) {
    error.message = getApiErrorMessage(error, fallback);
    throw error;
  }
};

export const dashboardApi = {
  getOverview: async (region, { cropName = 'lua' } = {}) => {
    return request(() => api.get('/api/dashboard/overview', {
      params: {
        region: region || undefined,
        crop_name: cropName,
      },
    }), 'Khong tai duoc dashboard overview');
  },

  getRealtimeStatus: async (region, { cropName = 'lua' } = {}) => {
    return request(() => api.get('/api/dashboard/realtime-status', {
      params: {
        region: region || undefined,
        crop_name: cropName,
      },
    }), 'Khong tai duoc realtime status');
  },

  getAiInsights: async (region, { cropName = 'lua' } = {}) => {
    return request(() => api.get('/api/dashboard/ai-insights', {
      params: {
        region: region || undefined,
        crop_name: cropName,
      },
    }), 'Khong tai duoc AI insights');
  },

  getRiskSummary: async (region, { cropName = 'lua' } = {}) => {
    return request(() => api.get('/api/dashboard/risk-summary', {
      params: {
        region: region || undefined,
        crop_name: cropName,
      },
    }), 'Khong tai duoc risk summary');
  },

  getActionToday: async (region, { cropName = 'lua' } = {}) => {
    return request(() => api.get('/api/dashboard/action-today', {
      params: {
        region: region || undefined,
        crop_name: cropName,
      },
    }), 'Khong tai duoc action today');
  },

  getSummary: async (region, { cropName = 'lua', forceRefresh = false } = {}) => {
    return request(() => api.get('/api/dashboard/summary', {
      params: {
        region: region || undefined,
        crop_name: cropName,
        force_refresh: forceRefresh,
      },
    }), 'Khong tai duoc dashboard summary');
  },

  getFeaturedCrop: async (region, { cropName = 'lua', forceRefresh = false } = {}) => {
    return request(() => api.get('/api/dashboard/featured-crop', {
      params: {
        region: region || undefined,
        crop_name: cropName,
        force_refresh: forceRefresh,
      },
    }), 'Khong tai duoc featured crop');
  },

  getPriceTrend: async ({ cropName = 'lua', region, days = 7 } = {}) => {
    return request(() => api.get('/api/dashboard/price-trend', {
      params: {
        crop_name: cropName,
        region: region || undefined,
        days,
      },
    }), 'Khong tai duoc price trend');
  },

  getWeatherOverview: async (region, { forceRefresh = false } = {}) => {
    return request(() => api.get('/api/dashboard/weather-overview', {
      params: {
        region: region || undefined,
        force_refresh: forceRefresh,
      },
    }), 'Khong tai duoc weather overview');
  },

  getWeatherRisk: async ({ region, cropName = 'lua', growthStage, forceRefresh = false } = {}) => {
    return request(() => api.get('/api/dashboard/weather-risk', {
      params: {
        region: region || undefined,
        crop_name: cropName,
        growth_stage: growthStage || undefined,
        force_refresh: forceRefresh,
      },
    }), 'Khong tai duoc weather risk');
  },

  getRegionalPrices: async ({ cropName = 'lua', regions, forceRefresh = false } = {}) => {
    return request(() => api.get('/api/dashboard/regional-prices', {
      params: {
        crop_name: cropName,
        regions,
        force_refresh: forceRefresh,
      },
      paramsSerializer: {
        indexes: null,
      },
    }), 'Khong tai duoc regional prices');
  },

  getRealtimeMarket: async ({ cropName = 'lua', region, forceRefresh = false } = {}) => {
    return request(() => api.get('/api/dashboard/realtime-market', {
      params: {
        crop_name: cropName,
        region: region || undefined,
        force_refresh: forceRefresh,
      },
    }), 'Khong tai duoc realtime market');
  },

  getNews: async ({ limit = 6, cropName, region, forceRefresh = false } = {}) => {
    return request(() => api.get('/api/dashboard/news', {
      params: {
        limit,
        crop_name: cropName || undefined,
        region: region || undefined,
        force_refresh: forceRefresh,
      },
    }), 'Khong tai duoc dashboard news');
  },

  getDataHealth: async ({ cropName = 'lua', region } = {}) => {
    return request(() => api.get('/api/dashboard/data-health', {
      params: {
        crop_name: cropName,
        region: region || undefined,
      },
    }), 'Khong tai duoc data health');
  },

  refresh: async ({ source = 'all', cropName = 'lua', region } = {}) => {
    return request(() => api.post('/api/dashboard/refresh', null, {
      params: {
        source,
        crop_name: cropName,
        region: region || undefined,
      },
    }), 'Khong refresh duoc dashboard');
  },

  reset: async ({ cropName = 'lua', region } = {}) => {
    return request(() => api.post('/api/dashboard/reset', null, {
      params: {
        crop_name: cropName,
        region: region || undefined,
      },
    }), 'Khong reset duoc dashboard');
  },

  getAiRecommendation: async ({ cropName = 'lua', region } = {}) => {
    return request(() => api.get('/api/dashboard/ai-recommendation', {
      params: {
        crop_name: cropName,
        region: region || undefined,
      },
    }), 'Khong tai duoc AI recommendation');
  },
};

dashboardApi.getDashboardOverview = dashboardApi.getOverview;
dashboardApi.getDashboardRealtimeStatus = dashboardApi.getRealtimeStatus;
dashboardApi.getAIInsights = dashboardApi.getAiInsights;
dashboardApi.getDashboardAIInsights = dashboardApi.getAiInsights;
dashboardApi.getDashboardRiskSummary = dashboardApi.getRiskSummary;
dashboardApi.getDashboardActionToday = dashboardApi.getActionToday;

dashboardApi.getDashboardFullData = async (region, { cropName = 'lua' } = {}) => {
  const results = await Promise.allSettled([
    dashboardApi.getDashboardOverview(region, { cropName }),
    dashboardApi.getRealtimeStatus(region, { cropName }),
    dashboardApi.getAIInsights(region, { cropName }),
    dashboardApi.getRiskSummary(region, { cropName }),
    dashboardApi.getActionToday(region, { cropName }),
  ]);
  const errors = results
    .map((result, index) => ({ result, key: ['overview', 'realtimeStatus', 'aiInsights', 'riskSummary', 'actionToday'][index] }))
    .filter(({ result }) => result.status === 'rejected')
    .map(({ result, key }) => ({ key, message: getApiErrorMessage(result.reason, `Khong tai duoc ${key}`) }));
  return {
    overview: settledValue(results[0], {
      region,
      crop_name: cropName,
      featured_crop: {},
      weather: {},
      weather_risk: {},
      forecast: [],
      regional_prices: [],
      news: [],
      realtime_market: {},
      alert_center: [],
      notifications: {},
      source: 'mock',
      source_name: 'Dashboard frontend fallback',
      fallback_used: true,
    }),
    realtimeStatus: settledValue(results[1], { api_status: [], source: 'mock', fallback_used: true }),
    aiInsights: settledValue(results[2], null),
    riskSummary: settledValue(results[3], {}),
    actionToday: settledValue(results[4], { actions: [], source: 'mock', fallback_used: true }),
    errors,
  };
};
