import api, { getApiErrorMessage, withApiTimeout } from './api';
import { normalizeApiError, normalizeApiResponse } from '../utils/apiResponse';

const request = async (factory, fallback) => {
  try {
    return normalizeApiResponse(await factory());
  } catch (error) {
    throw normalizeApiError({ ...error, message: getApiErrorMessage(error, fallback) });
  }
};

export const aiApi = {
  chat: async ({ question, crop, cropName, region, context, sessionId }) => {
    const selectedCrop = crop || cropName;
    const payload = {
      message: question,
      session_id: sessionId,
    };
    if (selectedCrop) {
      payload.crop = selectedCrop;
      payload.crop_name = selectedCrop;
    }
    if (region) payload.region = region;
    if (context) payload.context = context;
    return request(() => api.post('/api/ai-chat/message', payload, withApiTimeout('ai')), 'Không thể kết nối trợ lý AI. Vui lòng thử lại sau.');
  },

  getHistory: async (limit = 20) => {
    return request(() => api.get(`/api/ai-chat/history?limit=${limit}`), 'Không tải được lịch sử chat');
  },

  deleteMessage: async (convId) => {
    return request(() => api.delete(`/api/ai-chat/history/${convId}`), 'Không xóa được tin chat');
  },

  clearHistory: async () => {
    return request(() => api.delete('/api/ai-chat/history'), 'Không xóa được lịch sử chat');
  },
};
