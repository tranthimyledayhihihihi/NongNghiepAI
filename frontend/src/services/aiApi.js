import api from './api';

export const aiApi = {
  chat: async ({ question }) => {
    const response = await api.post('/api/chat/ask', { question }, { timeout: 90000 });
    return response.data;
  },

  getHistory: async (limit = 20) => {
    const response = await api.get(`/api/chat/history?limit=${limit}`);
    return response.data;
  },

  deleteMessage: async (convId) => {
    const response = await api.delete(`/api/chat/history/${convId}`);
    return response.data;
  },

  clearHistory: async () => {
    const response = await api.delete('/api/chat/history');
    return response.data;
  },
};
