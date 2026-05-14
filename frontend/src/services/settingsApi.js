import api from './api';

const unwrap = (response) => response.data?.data ?? response.data;

export const settingsApi = {
  getMe: async () => {
    const response = await api.get('/api/settings/me');
    return unwrap(response);
  },

  updateMe: async (payload) => {
    const response = await api.put('/api/settings/me', payload);
    return unwrap(response);
  },
};
