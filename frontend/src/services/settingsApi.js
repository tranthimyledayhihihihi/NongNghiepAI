import api from './api';

const unwrap = (response) => response.data?.data ?? response.data;

export const settingsApi = {
  getProfile: async () => {
    const response = await api.get('/api/settings/profile');
    return unwrap(response);
  },

  saveProfile: async (payload) => {
    const response = await api.post('/api/settings/profile', payload);
    return unwrap(response);
  },

  getFarm: async () => {
    const response = await api.get('/api/settings/farm');
    return unwrap(response);
  },

  saveFarm: async (payload) => {
    const response = await api.post('/api/settings/farm', payload);
    return unwrap(response);
  },

  getAlertPreferences: async () => {
    const response = await api.get('/api/settings/alert-preferences');
    return unwrap(response);
  },

  saveAlertPreferences: async (payload) => {
    const response = await api.post('/api/settings/alert-preferences', payload);
    return unwrap(response);
  },

  getAiPreferences: async () => {
    const response = await api.get('/api/settings/ai-preferences');
    return unwrap(response);
  },

  saveAiPreferences: async (payload) => {
    const response = await api.post('/api/settings/ai-preferences', payload);
    return unwrap(response);
  },

  testNotificationChannel: async ({ channel, receiver }) => {
    const response = await api.post('/api/settings/test-notification-channel', { channel, receiver });
    return unwrap(response);
  },

  getMe: async () => {
    const response = await api.get('/api/settings/me');
    return unwrap(response);
  },

  updateMe: async (payload) => {
    const response = await api.put('/api/settings/me', payload);
    return unwrap(response);
  },

  getLocations: async () => {
    const response = await api.get('/api/locations');
    return unwrap(response);
  },

  getChannelStatus: async () => {
    const response = await api.get('/api/settings/channels/status');
    return unwrap(response);
  },

  testChannel: async ({ channel, receiver }) => {
    const response = await api.post('/api/settings/channels/test', { channel, receiver });
    return unwrap(response);
  },

  sendTestNotification: async ({ channel, receiver }) => {
    const response = await api.post('/api/notifications/test', { channel, receiver });
    return unwrap(response);
  },

  startTwoFactor: async ({ method }) => {
    const response = await api.post('/api/settings/2fa/start', { method });
    return unwrap(response);
  },

  verifyTwoFactor: async ({ challengeId, code }) => {
    const response = await api.post('/api/settings/2fa/verify', {
      challenge_id: challengeId,
      code,
    });
    return unwrap(response);
  },

  disableTwoFactor: async () => {
    const response = await api.post('/api/settings/2fa/disable');
    return unwrap(response);
  },

  changePassword: async ({ oldPassword, newPassword }) => {
    const response = await api.post('/api/settings/password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return unwrap(response);
  },
};
