import api from './api';

export const qualityApi = {
  // Check quality from image
  checkQuality: async (imageFile) => {
    const formData = new FormData();
    formData.append('file', imageFile);

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
};
