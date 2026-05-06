import api from './api';

export const alertApi = {
  // Get user alerts
  getAlerts: async () => {
    const response = await api.get('/api/alert/list');
    return response.data;
  },

  createPriceAlert: async ({
    cropName,
    region,
    targetPrice,
    condition = 'above',
    notificationChannel = 'email',
    receiver,
  }) => {
    const response = await api.post('/api/alert/create', {
      crop_name: cropName,
      region,
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
};
