import api from './api';
import { unwrapApiResponse } from '../utils/apiResponse';

export const harvestApi = {
  forecastHarvest: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/forecast', {
      crop_name: cropName,
      planting_date: plantingDate,
      region,
    });
    return unwrapApiResponse(response);
  },

  optimizeHarvest: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/optimize', {
      crop_name: cropName,
      planting_date: plantingDate,
      region,
    });
    return unwrapApiResponse(response);
  },

  getCalendar: async () => {
    const response = await api.get('/api/harvest/calendar');
    return unwrapApiResponse(response);
  },

  getRisk: async (seasonId) => {
    const response = await api.get(`/api/harvest/risk/${encodeURIComponent(seasonId)}`);
    return unwrapApiResponse(response);
  },

  recalculate: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/recalculate', {
      crop_name: cropName,
      planting_date: plantingDate,
      region,
    });
    return unwrapApiResponse(response);
  },

  predictHarvest: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/predict', {
      crop_name: cropName,
      planting_date: plantingDate,
      region,
    });
    const data = unwrapApiResponse(response);
    return {
      ...data,
      predicted_harvest_date: data.predicted_harvest_date || data.expected_harvest_date,
    };
  },

  getHistory: async (userId = 1, limit = 50) => {
    const response = await api.get(`/api/harvest/history/${encodeURIComponent(userId)}`, {
      params: { limit },
    });
    return unwrapApiResponse(response);
  },

  getSchedules: async (userId = 1, limit = 50) => {
    const response = await api.get(`/api/harvest/schedules/${encodeURIComponent(userId)}`, {
      params: { limit },
    });
    return unwrapApiResponse(response);
  },

  getMyHistory: async (limit = 50) => {
    const response = await api.get('/api/harvest/history/me', {
      params: { limit },
    });
    return unwrapApiResponse(response);
  },

  getMySchedules: async (limit = 50) => {
    const response = await api.get('/api/harvest/schedules/me', {
      params: { limit },
    });
    return unwrapApiResponse(response);
  },

  createSchedule: async (payload) => {
    const response = await api.post('/api/harvest/schedules', payload);
    return unwrapApiResponse(response);
  },
};
