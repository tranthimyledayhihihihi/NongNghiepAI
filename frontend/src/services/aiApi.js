import api from './api';

export const aiApi = {
  chat: async ({ question, cropName, region, sessionId }) => {
    const response = await api.post('/api/ai-chat/message', {
      message: question,
      crop_name: cropName,
      region,
      session_id: sessionId,
    }, { timeout: 90000 });
    return response.data;
  },

  getHistory: async (limit = 20) => {
    const response = await api.get(`/api/ai-chat/history?limit=${limit}`);
    return response.data?.data ?? response.data;
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
