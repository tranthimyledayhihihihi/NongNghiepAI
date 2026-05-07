import api from './api';

export const aiApi = {
  chat: async ({ question, cropName, region, userId, sessionId }) => {
    const response = await api.post('/api/ai/chat', {
      question,
      crop_name: cropName,
      region,
      user_id: userId,
      session_id: sessionId,
    });
    return response.data;
  },
};
