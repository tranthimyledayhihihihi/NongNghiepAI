import api from './api';

export const alertApi = {
  getOptions: async () => {
    const response = await api.get('/api/alert/options');
    return response.data;
  },

  getCurrentPrice: async ({ cropName, cropId, region, regionKey, forceRefresh = true }) => {
    const response = await api.get('/api/prices/current', {
      params: {
        crop_name: cropName || undefined,
        crop_id: cropId || undefined,
        region: region || undefined,
        region_key: regionKey || undefined,
        force_refresh: forceRefresh,
      },
    });
    return response.data;
  },

  getSuggestions: async ({ cropName, cropId, region, regionKey }) => {
    const response = await api.get('/api/alert/suggestions', {
      params: {
        crop_name: cropName || undefined,
        crop_id: cropId || undefined,
        region: region || undefined,
        region_key: regionKey || undefined,
      },
    });
    return response.data;
  },

  // Get user alerts
  getAlerts: async () => {
    const response = await api.get('/api/alert/list');
    return response.data;
  },

  getTriggers: async () => {
    const response = await api.get('/api/alert/triggers');
    return response.data;
  },

  createPriceAlert: async ({
    cropName,
    cropId,
    region,
    regionKey,
    targetPrice,
    condition = 'above',
    notificationChannel = 'email',
    receiver,
  }) => {
    const response = await api.post('/api/alert/create', {
      crop_name: cropName,
      crop_id: cropId,
      region,
      region_key: regionKey,
      target_price: Number(targetPrice),
      condition,
      notification_channel: notificationChannel,
      receiver,
    });
    return response.data;
  },

  // Backward-compatible alias for older components
  subscribe: async (cropName, region, targetPrice, notifyMethod, contact) => {
    const response = await api.post('/api/alert/create', {
      crop_name: cropName,
      region,
      target_price: Number(targetPrice),
      condition: 'above',
      notification_channel: notifyMethod,
      receiver: contact,
    });
    return response.data;
  },

  deactivate: async (alertId) => {
    const response = await api.delete(`/api/alert/${alertId}`);
    return response.data;
  },

  unsubscribe: async (alertId) => {
    const response = await api.delete(`/api/alert/${alertId}`);
    return response.data;
  },

  checkNow: async () => {
    const response = await api.post('/api/alert/check');
    return response.data;
  },

  getWeatherAlerts: async (region) => {
    const response = await api.get(`/api/weather/alerts/${encodeURIComponent(region)}`);
    return response.data;
  },

  createWeatherAlert: async (payload) => {
    const response = await api.post('/api/weather-alert/create', payload);
    return response.data;
  },

  deactivateWeather: async (alertId) => {
    const response = await api.delete(`/api/weather-alert/${alertId}`);
    return response.data;
  },
};
