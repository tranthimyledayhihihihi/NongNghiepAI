import api, { getApiErrorMessage, withApiTimeout } from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

const request = async (factory, fallback) => {
  try {
    return normalizeApiResponse(await factory());
  } catch (error) {
    error.message = getApiErrorMessage(error, fallback);
    throw error;
  }
};

export const aiApi = {
  chat: async ({ question, crop, cropName, region, context, sessionId }) => {
    const selectedCrop = crop || cropName;
    return request(() => api.post('/api/ai-chat/message', {
      message: question,
      crop: selectedCrop,
      crop_name: selectedCrop,
      region,
      context,
      session_id: sessionId,
    }, withApiTimeout('ai')), 'Khong goi duoc AI chat');
  },

  getHistory: async (limit = 20) => {
    return request(() => api.get(`/api/ai-chat/history?limit=${limit}`), 'Khong tai duoc lich su chat');
  },

  deleteMessage: async (convId) => {
    return request(() => api.delete(`/api/chat/history/${convId}`), 'Khong xoa duoc tin chat');
  },

  clearHistory: async () => {
    return request(() => api.delete('/api/chat/history'), 'Khong xoa duoc lich su chat');
  },
};
