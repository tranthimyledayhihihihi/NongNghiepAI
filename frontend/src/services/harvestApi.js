import api from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

export const harvestApi = {
  forecastHarvest: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/forecast', {
      crop_name: cropName,
      planting_date: plantingDate,
      region,
    });
    return normalizeApiResponse(response);
  },

  optimizeHarvest: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/optimize', {
      crop_name: cropName,
      planting_date: plantingDate,
      region,
    });
    return normalizeApiResponse(response);
  },

  getCalendar: async () => {
    const response = await api.get('/api/harvest/calendar');
    return normalizeApiResponse(response);
  },

  getRisk: async (seasonId) => {
    const response = await api.get(`/api/harvest/risk/${encodeURIComponent(seasonId)}`);
    return normalizeApiResponse(response);
  },

  recalculate: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/recalculate', {
      crop_name: cropName,
      planting_date: plantingDate,
      region,
    });
    return normalizeApiResponse(response);
  },

  predictHarvest: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/predict', {
      crop_name: cropName,
      planting_date: plantingDate,
      region,
    });
    const data = normalizeApiResponse(response);
    return {
      ...data,
      predicted_harvest_date: data.predicted_harvest_date || data.expected_harvest_date,
    };
  },

  getHistory: async (userId = 1, limit = 50) => {
    const response = await api.get(`/api/harvest/history/${encodeURIComponent(userId)}`, {
      params: { limit },
    });
    return normalizeApiResponse(response);
  },

  getSchedules: async (userId = 1, limit = 50) => {
    const response = await api.get(`/api/harvest/schedules/${encodeURIComponent(userId)}`, {
      params: { limit },
    });
    return normalizeApiResponse(response);
  },

  getMyHistory: async (limit = 50) => {
    const response = await api.get('/api/harvest/history/me', {
      params: { limit },
    });
    return normalizeApiResponse(response);
  },

  getMySchedules: async (limit = 50) => {
    const response = await api.get('/api/harvest/schedules/me', {
      params: { limit },
    });
    return normalizeApiResponse(response);
  },

  createSchedule: async (payload) => {
    const response = await api.post('/api/harvest/schedules', payload);
    return normalizeApiResponse(response);
  },
};
