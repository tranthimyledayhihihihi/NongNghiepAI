import api, { getApiErrorMessage } from './api';
import { normalizeApiError, unwrapApiResponse } from '../utils/apiResponse';

const unwrap = (response) => unwrapApiResponse(response);
const request = async (factory, fallback) => {
  try {
    return unwrap(await factory());
  } catch (error) {
    throw normalizeApiError({ ...error, message: getApiErrorMessage(error, fallback) });
  }
};

export const settingsApi = {
  getProfile: async () => {
    return request(() => api.get('/api/settings/profile'), 'Không tải được hồ sơ cài đặt');
  },

  saveProfile: async (payload) => {
    return request(() => api.post('/api/settings/profile', payload), 'Không lưu được hồ sơ cài đặt');
  },

  getFarm: async () => {
    return request(() => api.get('/api/settings/farm'), 'Không tải được thông tin trang trại');
  },

  saveFarm: async (payload) => {
    return request(() => api.post('/api/settings/farm', payload), 'Không lưu được thông tin trang trại');
  },

  getAlertPreferences: async () => {
    return request(() => api.get('/api/settings/alert-preferences'), 'Không tải được tùy chọn cảnh báo');
  },

  saveAlertPreferences: async (payload) => {
    return request(() => api.post('/api/settings/alert-preferences', payload), 'Không lưu được tùy chọn cảnh báo');
  },

  getAiPreferences: async () => {
    return request(() => api.get('/api/settings/ai-preferences'), 'Không tải được tùy chọn AI');
  },

  saveAiPreferences: async (payload) => {
    return request(() => api.post('/api/settings/ai-preferences', payload), 'Không lưu được tùy chọn AI');
  },

  testNotificationChannel: async ({ channel, receiver }) => {
    return request(() => api.post('/api/settings/test-notification-channel', { channel, receiver }), 'Không kiểm tra được kênh thông báo');
  },

  getMe: async () => {
    return request(() => api.get('/api/settings/me'), 'Không tải được cài đặt');
  },

  updateMe: async (payload) => {
    return request(() => api.put('/api/settings/me', payload), 'Không lưu được cài đặt');
  },

  getLocations: async () => {
    return request(() => api.get('/api/locations'), 'Không tải được danh sách khu vực');
  },

  getChannelStatus: async () => {
    return request(() => api.get('/api/settings/channels/status'), 'Không tải được trạng thái kênh');
  },

  testChannel: async ({ channel, receiver }) => {
    return request(() => api.post('/api/settings/channels/test', { channel, receiver }), 'Không kiểm tra được kênh thông báo');
  },

  sendTestNotification: async ({ channel, receiver }) => {
    return request(() => api.post('/api/notifications/test', { channel, receiver }), 'Không gửi được thông báo thử');
  },

  startTwoFactor: async ({ method }) => {
    return request(() => api.post('/api/settings/2fa/start', { method }), 'Không bắt đầu được 2FA');
  },

  verifyTwoFactor: async ({ challengeId, code }) => {
    return request(() => api.post('/api/settings/2fa/verify', {
      challenge_id: challengeId,
      code,
    }), 'Không xác minh được 2FA');
  },

  disableTwoFactor: async () => {
    return request(() => api.post('/api/settings/2fa/disable'), 'Không tắt được 2FA');
  },

  changePassword: async ({ oldPassword, newPassword }) => {
    return request(() => api.post('/api/settings/password', {
      old_password: oldPassword,
      new_password: newPassword,
    }), 'Không đổi được mật khẩu');
  },
};

settingsApi.getProfileSettings = settingsApi.getProfile;
settingsApi.saveProfileSettings = settingsApi.saveProfile;
settingsApi.getFarmSettings = settingsApi.getFarm;
settingsApi.saveFarmSettings = settingsApi.saveFarm;
settingsApi.getAIPreferences = settingsApi.getAiPreferences;
settingsApi.saveAIPreferences = settingsApi.saveAiPreferences;
