import api from './api';

export const alertApi = {
  // Get user alerts
  getAlerts: async () => {
    const response = await api.get('/api/alerts');
    return response.data;
  },

  // Subscribe to price alerts
  subscribe: async (cropName, region, threshold, notifyMethod, contact) => {
    const response = await api.post('/api/alerts/subscribe', {
      crop_name: cropName,
      region: region,
      price_change_threshold: threshold,
      notify_method: notifyMethod,
      contact: contact,
    });
    return response.data;
  },

  // Unsubscribe from alerts
  unsubscribe: async (subscriptionId) => {
    const response = await api.delete(`/api/alerts/subscribe/${subscriptionId}`);
    return response.data;
  },
};
