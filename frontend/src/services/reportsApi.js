import api from './api';

const unwrap = (response) => response.data?.data ?? response.data;

export const reportsApi = {
  getSummary: async (limit = 100) => {
    const response = await api.get('/api/reports/summary', {
      params: { limit },
    });
    return unwrap(response);
  },
};
