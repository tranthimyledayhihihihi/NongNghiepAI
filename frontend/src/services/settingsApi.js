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

export const settingsApi = {
  getProfile: async () => {
    return request(() => api.get('/api/settings/profile'), 'Khong tai duoc profile settings');
  },

  saveProfile: async (payload) => {
    return request(() => api.post('/api/settings/profile', payload), 'Khong luu duoc profile settings');
  },

  getFarm: async () => {
    return request(() => api.get('/api/settings/farm'), 'Khong tai duoc farm settings');
  },

  saveFarm: async (payload) => {
    return request(() => api.post('/api/settings/farm', payload), 'Khong luu duoc farm settings');
  },

  getAlertPreferences: async () => {
    return request(() => api.get('/api/settings/alert-preferences'), 'Khong tai duoc alert preferences');
  },

  saveAlertPreferences: async (payload) => {
    return request(() => api.post('/api/settings/alert-preferences', payload), 'Khong luu duoc alert preferences');
  },

  getAiPreferences: async () => {
    return request(() => api.get('/api/settings/ai-preferences'), 'Khong tai duoc AI preferences');
  },

  saveAiPreferences: async (payload) => {
    return request(() => api.post('/api/settings/ai-preferences', payload), 'Khong luu duoc AI preferences');
  },

  testNotificationChannel: async ({ channel, receiver }) => {
    return request(() => api.post('/api/settings/test-notification-channel', { channel, receiver }), 'Khong test duoc kenh thong bao');
  },

  getMe: async () => {
    return request(() => api.get('/api/settings/me'), 'Khong tai duoc settings legacy');
  },

  updateMe: async (payload) => {
    return request(() => api.put('/api/settings/me', payload), 'Khong luu duoc settings legacy');
  },

  getLocations: async () => {
    return request(() => api.get('/api/locations'), 'Khong tai duoc danh sach khu vuc');
  },

  getChannelStatus: async () => {
    return request(() => api.get('/api/settings/channels/status'), 'Khong tai duoc trang thai kenh');
  },

  testChannel: async ({ channel, receiver }) => {
    return request(() => api.post('/api/settings/channels/test', { channel, receiver }), 'Khong test duoc kenh legacy');
  },

  sendTestNotification: async ({ channel, receiver }) => {
    return request(() => api.post('/api/notifications/test', { channel, receiver }), 'Khong gui duoc thong bao test');
  },

  startTwoFactor: async ({ method }) => {
    return request(() => api.post('/api/settings/2fa/start', { method }), 'Khong bat dau duoc 2FA');
  },

  verifyTwoFactor: async ({ challengeId, code }) => {
    return request(() => api.post('/api/settings/2fa/verify', {
      challenge_id: challengeId,
      code,
    }), 'Khong xac minh duoc 2FA');
  },

  disableTwoFactor: async () => {
    return request(() => api.post('/api/settings/2fa/disable'), 'Khong tat duoc 2FA');
  },

  changePassword: async ({ oldPassword, newPassword }) => {
    return request(() => api.post('/api/settings/password', {
      old_password: oldPassword,
      new_password: newPassword,
    }), 'Khong doi duoc mat khau');
  },
};

settingsApi.getProfileSettings = settingsApi.getProfile;
settingsApi.saveProfileSettings = settingsApi.saveProfile;
settingsApi.getFarmSettings = settingsApi.getFarm;
settingsApi.saveFarmSettings = settingsApi.saveFarm;
settingsApi.getAIPreferences = settingsApi.getAiPreferences;
settingsApi.saveAIPreferences = settingsApi.saveAiPreferences;
