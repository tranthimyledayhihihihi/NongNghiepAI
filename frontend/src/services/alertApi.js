import api from './api';

const unwrap = (response) => response.data?.data ?? response.data;

export const alertApi = {
  getOptions: async () => {
    const response = await api.get('/api/alert/options');
    return unwrap(response);
  },

  getCurrentPrice: async ({ cropName, cropId, region, regionKey, forceRefresh = true }) => {
    const response = await api.get('/api/pricing/current', {
      params: {
        crop_name: cropName || undefined,
        region: region || undefined,
        quality_grade: 'grade_1',
        force_refresh: forceRefresh,
        crop_id: cropId || undefined,
        region_key: regionKey || undefined,
      },
    });
    return unwrap(response);
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
    return unwrap(response);
  },

  // Get user alerts
  getAlerts: async () => {
    const response = await api.get('/api/alerts/list');
    return unwrap(response);
  },

  getTriggers: async () => {
    const response = await api.get('/api/alert/triggers');
    return unwrap(response);
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
    const response = await api.post('/api/alerts/create', {
      alert_type: 'price',
      crop_name: cropName,
      crop_id: cropId,
      region,
      region_key: regionKey,
      target_price: Number(targetPrice),
      condition,
      notification_channel: notificationChannel,
      receiver,
    });
    return unwrap(response);
  },

  // Backward-compatible alias for older components
  subscribe: async (cropName, region, targetPrice, notifyMethod, contact) => {
    const response = await api.post('/api/alerts/create', {
      alert_type: 'price',
      crop_name: cropName,
      region,
      target_price: Number(targetPrice),
      condition: 'above',
      notification_channel: notifyMethod,
      receiver: contact,
    });
    return unwrap(response);
  },

  deactivate: async (alertId) => {
    const response = await api.delete(`/api/alert/${alertId}`);
    return unwrap(response);
  },

  unsubscribe: async (alertId) => {
    const response = await api.delete(`/api/alert/${alertId}`);
    return unwrap(response);
  },

  checkNow: async () => {
    const response = await api.post('/api/alerts/evaluate');
    return unwrap(response);
  },

  autoGenerate: async ({ cropName = 'lua', region = 'Ha Noi', alertType = 'weather' } = {}) => {
    const response = await api.post('/api/alerts/auto-generate', {
      alert_type: alertType,
      crop_name: cropName,
      region,
    });
    return unwrap(response);
  },

  sendSmartAlert: async (payload) => {
    const response = await api.post('/api/alerts/send', payload);
    return unwrap(response);
  },

  testChannel: async ({ channel, receiver }) => {
    const response = await api.post('/api/alerts/test-channel', { channel, receiver });
    return unwrap(response);
  },

  getWeatherAlerts: async (region) => {
    const response = await api.get(`/api/weather/alerts/${encodeURIComponent(region)}`);
    return unwrap(response);
  },

  createWeatherAlert: async (payload) => {
    const response = await api.post('/api/alerts/create', {
      alert_type: 'weather',
      region: payload.region,
      region_key: payload.region_key,
      condition: payload.condition,
      target_price: payload.threshold,
      severity: payload.severity,
      notification_channel: payload.notification_channel,
      receiver: payload.receiver,
      recommended_action: payload.recommended_action,
    });
    return unwrap(response);
  },

  deactivateWeather: async (alertId) => {
    const response = await api.delete(`/api/weather-alert/${alertId}`);
    return unwrap(response);
  },
};
