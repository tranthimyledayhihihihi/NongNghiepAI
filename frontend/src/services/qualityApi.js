import api from './api';

export const qualityApi = {
  // Check quality from image
  checkQuality: async (imageFile, cropName = 'ca chua', region = 'Ha Noi') => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('crop_name', cropName);
    formData.append('region', region);

    const response = await api.post('/api/quality/check', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get quality grades info
  getQualityGrades: async () => {
    const response = await api.get('/api/quality/grades');
    return response.data;
  },

  getHistory: async (userId = 1, limit = 50) => {
    const response = await api.get(`/api/quality/history/${encodeURIComponent(userId)}`, {
      params: { limit },
    });
    return response.data;
  },
};
