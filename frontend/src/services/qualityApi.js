import api, { withApiTimeout } from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

export const qualityApi = {
  checkQuality: async (imageFile, cropName = 'ca chua', region = 'Ha Noi') => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('crop_name', cropName);
    formData.append('region', region);

    const response = await api.post('/api/quality/check', formData, withApiTimeout('upload', {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }));
    return normalizeApiResponse(response);
  },

  checkWithPrice: async (imageFile, cropName = 'ca chua', region = 'Ha Noi') => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('crop_name', cropName);
    formData.append('region', region);

    const response = await api.post('/api/quality/check-with-price', formData, withApiTimeout('upload', {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }));
    return normalizeApiResponse(response);
  },

  getQualityGrades: async () => {
    const response = await api.get('/api/quality/grades');
    return normalizeApiResponse(response);
  },

  getHistory: async (userId = 1, limit = 50) => {
    const response = await api.get(`/api/quality/history/${encodeURIComponent(userId)}`, {
      params: { limit },
    });
    return normalizeApiResponse(response);
  },
};
