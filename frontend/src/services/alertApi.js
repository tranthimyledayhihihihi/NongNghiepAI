import api, { getApiErrorMessage } from './api';
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

export const alertApi = {
  getOptions: async () => {
    return request(() => api.get('/api/alerts/options'), 'Khong tai duoc alert options');
  },

  getCurrentPrice: async ({ cropName, cropId, region, regionKey, forceRefresh = true }) => {
    return request(() => api.get('/api/pricing/current', {
      params: {
        crop_name: cropName || undefined,
        region: region || undefined,
        quality_grade: 'grade_1',
        force_refresh: forceRefresh,
        crop_id: cropId || undefined,
        region_key: regionKey || undefined,
      },
    }), 'Khong tai duoc gia hien tai');
  },

  getSuggestions: async ({ cropName, cropId, region, regionKey }) => {
    return request(() => api.get('/api/alerts/suggestions', {
      params: {
        crop_name: cropName || undefined,
        crop_id: cropId || undefined,
        region: region || undefined,
        region_key: regionKey || undefined,
      },
    }), 'Khong tai duoc goi y canh bao');
  },

  // Get user alerts
  getAlerts: async (params = {}) => {
    return request(() => api.get('/api/alerts/list', { params }), 'Khong tai duoc danh sach canh bao thong minh');
  },

  getTriggers: async () => {
    return request(() => api.get('/api/alerts/triggers'), 'Khong tai duoc lich su trigger');
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
    sendChannels,
  }) => {
    return request(() => api.post('/api/alerts/create', {
      alert_type: 'price',
      crop_name: cropName,
      crop_id: cropId,
      region,
      region_key: regionKey,
      target_price: Number(targetPrice),
      condition,
      notification_channel: notificationChannel,
      send_channels: sendChannels || [notificationChannel || 'app'],
      receiver,
    }), 'Khong tao duoc canh bao gia');
  },

  // Backward-compatible alias for older components
  subscribe: async (cropName, region, targetPrice, notifyMethod, contact) => {
    return request(() => api.post('/api/alerts/create', {
      alert_type: 'price',
      crop_name: cropName,
      region,
      target_price: Number(targetPrice),
      condition: 'above',
      notification_channel: notifyMethod,
      send_channels: [notifyMethod || 'app'],
      receiver: contact,
    }), 'Khong dang ky duoc canh bao');
  },

  deactivate: async (alertId) => {
    return request(() => api.delete(`/api/alerts/${alertId}`), 'Khong tat duoc canh bao');
  },

  unsubscribe: async (alertId) => {
    return request(() => api.delete(`/api/alerts/${alertId}`), 'Khong huy duoc canh bao');
  },

  checkNow: async (payload = {}) => {
    return request(() => api.post('/api/alerts/evaluate', payload), 'Khong danh gia duoc canh bao');
  },

  autoGenerate: async ({ cropName = 'lua', region = 'Ha Noi', alertType = 'weather' } = {}) => {
    return request(() => api.post('/api/alerts/auto-generate', {
      alert_type: alertType,
      crop_name: cropName,
      region,
    }), 'Khong auto-generate duoc canh bao');
  },

  sendSmartAlert: async (payload) => {
    return request(() => api.post('/api/alerts/send', payload), 'Khong gui duoc canh bao thong minh');
  },

  testChannel: async ({ channel, receiver }) => {
    return request(() => api.post('/api/alerts/test-channel', { channel, receiver }), 'Khong test duoc kenh canh bao');
  },

  getWeatherAlerts: async (region) => {
    return request(() => api.get(`/api/weather/alerts/${encodeURIComponent(region)}`), 'Khong tai duoc canh bao thoi tiet');
  },

  createWeatherAlert: async (payload) => {
    return request(() => api.post('/api/alerts/create', {
      alert_type: 'weather',
      region: payload.region,
      region_key: payload.region_key,
      condition: payload.condition,
      target_price: payload.threshold,
      severity: payload.severity,
      notification_channel: payload.notification_channel,
      receiver: payload.receiver,
      recommended_action: payload.recommended_action,
      send_channels: payload.send_channels || [payload.notification_channel || 'app'],
    }), 'Khong tao duoc canh bao thoi tiet');
  },

  deactivateWeather: async (alertId) => {
    return request(() => api.delete(`/api/weather-alert/${alertId}`), 'Khong tat duoc canh bao thoi tiet');
  },
};

alertApi.createSmartAlert = (payload) => request(() => api.post('/api/alerts/create', payload), 'Khong tao duoc smart alert');
alertApi.getSmartAlerts = alertApi.getAlerts;
alertApi.evaluateAlerts = alertApi.checkNow;
alertApi.autoGenerateAlerts = (payload = {}) => request(() => api.post('/api/alerts/auto-generate', payload), 'Khong auto-generate duoc smart alert');
alertApi.sendAlert = alertApi.sendSmartAlert;
alertApi.testAlertChannel = alertApi.testChannel;
