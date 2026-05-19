import api from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

const unwrap = (response) => normalizeApiResponse(response);

export const reportsApi = {
  getSummary: async (limit = 100) => {
    const response = await api.get('/api/reports/summary', {
      params: { limit },
    });
    return unwrap(response);
  },
};
