import api from './api';
import { unwrapApiResponse } from '../utils/apiResponse';

const unwrap = (response) => unwrapApiResponse(response);

export const reportsApi = {
  getSummary: async (limit = 100) => {
    const response = await api.get('/api/reports/summary', {
      params: { limit },
    });
    return unwrap(response);
  },
};
