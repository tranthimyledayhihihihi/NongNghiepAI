import api from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

const unwrap = (response) => normalizeApiResponse(response);

export const seasonApi = {
  getSeasons: async (params = {}) => {
    const response = await api.get('/api/seasons', { params });
    return unwrap(response);
  },

  getActiveSeasons: async () => {
    const response = await api.get('/api/seasons/active');
    return unwrap(response);
  },

  getSeasonById: async (id) => {
    const response = await api.get(`/api/seasons/${encodeURIComponent(id)}`);
    return unwrap(response);
  },

  createSeason: async (data) => {
    const response = await api.post('/api/seasons', data);
    return unwrap(response);
  },

  updateSeason: async (id, data) => {
    const response = await api.put(`/api/seasons/${encodeURIComponent(id)}`, data);
    return unwrap(response);
  },

  deleteSeason: async (id) => {
    const response = await api.delete(`/api/seasons/${encodeURIComponent(id)}`);
    return unwrap(response);
  },

  completeSeason: async (id) => {
    const response = await api.patch(`/api/seasons/${encodeURIComponent(id)}/complete`);
    return unwrap(response);
  },

  predictHarvestDate: async (data) => {
    const response = await api.post('/api/seasons/predict-harvest-date', data);
    return unwrap(response);
  },

  getSeasonSummary: async () => {
    const response = await api.get('/api/seasons/stats/summary');
    return unwrap(response);
  },
};
