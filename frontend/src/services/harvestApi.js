import api from './api';

export const harvestApi = {
  forecastHarvest: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/forecast', {
      crop_name: cropName,
      planting_date: plantingDate,
      region: region,
    });
    return response.data;
  },

  predictHarvest: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/predict', null, {
      params: {
        crop_name: cropName,
        planting_date: plantingDate,
        region,
      },
    });
    return {
      ...response.data,
      predicted_harvest_date: response.data.predicted_harvest_date || response.data.expected_harvest_date,
    };
  },

  getHistory: async (userId = 1, limit = 50) => {
    const response = await api.get(`/api/harvest/history/${encodeURIComponent(userId)}`, {
      params: { limit },
    });
    return response.data;
  },

  getSchedules: async (userId = 1, limit = 50) => {
    const response = await api.get(`/api/harvest/schedules/${encodeURIComponent(userId)}`, {
      params: { limit },
    });
    return response.data;
  },
};
