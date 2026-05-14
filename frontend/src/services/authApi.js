import api from './api';

export const authApi = {
  login: async ({ email, password }) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },

  register: async ({ fullName, email, password, phoneNumber, zaloId, region }) => {
    const response = await api.post('/api/auth/register', {
      full_name: fullName,
      email,
      password,
      phone_number: phoneNumber || null,
      zalo_id: zaloId || null,
      region: region || null,
    });
    return response.data;
  },

  me: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};
