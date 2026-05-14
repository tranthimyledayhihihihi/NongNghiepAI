import api from './api';

export const aiApi = {
  chat: async ({ question }) => {
    const response = await api.post('/api/chat/price-qa', { question }, { timeout: 90000 });
    return response.data;
  },

  getHistory: async (limit = 20) => {
    const response = await api.get(`/api/chat/history?limit=${limit}`);
    return response.data;
  },
};
