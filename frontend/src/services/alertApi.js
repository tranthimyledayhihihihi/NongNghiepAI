import api, { getApiErrorMessage } from './api';
import { normalizeApiError, normalizeApiResponse } from '../utils/apiResponse';

const unwrap = (response) => normalizeApiResponse(response);
const request = async (factory, fallback) => {
  try {
    return unwrap(await factory());
  } catch (error) {
    throw normalizeApiError({ ...error, message: getApiErrorMessage(error, fallback) });
  }
};

export const alertApi = {
  getOptions: async () => {
    return request(() => api.get('/api/alerts/options'), 'Không tải được tùy chọn cảnh báo');
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
    }), 'Không thể tải giá realtime');
  },

  getSuggestions: async ({ cropName, cropId, region, regionKey }) => {
    return request(() => api.get('/api/alerts/suggestions', {
      params: {
        crop_name: cropName || undefined,
        crop_id: cropId || undefined,
        region: region || undefined,
        region_key: regionKey || undefined,
      },
    }), 'Không tải được gợi ý cảnh báo');
  },

  // Get user alerts
  getAlerts: async (params = {}) => {
    return request(() => api.get('/api/alerts/list', { params }), 'Không tải được danh sách cảnh báo');
  },

  getTriggers: async () => {
    return request(() => api.get('/api/alerts/triggers'), 'Không tải được lịch sử kích hoạt');
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
    }), 'Không tạo được cảnh báo giá');
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
    }), 'Không đăng ký được cảnh báo');
  },

  deactivate: async (alertId) => {
    return request(() => api.delete(`/api/alerts/${alertId}`), 'Không tắt được cảnh báo');
  },

  unsubscribe: async (alertId) => {
    return request(() => api.delete(`/api/alerts/${alertId}`), 'Không hủy được cảnh báo');
  },

  checkNow: async (payload = {}) => {
    return request(() => api.post('/api/alerts/evaluate', payload), 'Không đánh giá được cảnh báo');
  },

  autoGenerate: async ({ cropName = 'lua', region = 'Ha Noi', alertType = 'weather' } = {}) => {
    return request(() => api.post('/api/alerts/auto-generate', {
      alert_type: alertType,
      crop_name: cropName,
      region,
    }), 'Không tự tạo được cảnh báo');
  },

  sendSmartAlert: async (payload) => {
    return request(() => api.post('/api/alerts/send', payload), 'Không gửi được cảnh báo');
  },

  testChannel: async ({ channel, receiver }) => {
    return request(() => api.post('/api/alerts/test-channel', { channel, receiver }), 'Không kiểm tra được kênh cảnh báo');
  },

  getWeatherAlerts: async (region) => {
    return request(() => api.get(`/api/weather/alerts/${encodeURIComponent(region)}`), 'Không tải được cảnh báo thời tiết');
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
    }), 'Không tạo được cảnh báo thời tiết');
  },

  deactivateWeather: async (alertId) => {
    return request(() => api.delete(`/api/weather-alert/${alertId}`), 'Không tắt được cảnh báo thoi tiet');
  },
};

alertApi.createSmartAlert = (payload) => request(() => api.post('/api/alerts/create', payload), 'Không tạo được cảnh báo thông minh');
alertApi.getSmartAlerts = alertApi.getAlerts;
alertApi.evaluateAlerts = alertApi.checkNow;
alertApi.autoGenerateAlerts = (payload = {}) => request(() => api.post('/api/alerts/auto-generate', payload), 'Không tự tạo được cảnh báo thông minh');
alertApi.sendAlert = alertApi.sendSmartAlert;
alertApi.testAlertChannel = alertApi.testChannel;

